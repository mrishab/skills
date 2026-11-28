#!/usr/bin/env python3
"""
Fetch and triage SonarQube issues for Java and Spring Boot projects.
Loads canonical rule definitions from references/rules.json (with optional
repo-local .sonar-triage.json overrides) and categorizes issues into
actionable fixes, preserved patterns, conditional review items, and unclassified.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent / "references" / "rules.json"
LOCAL_OVERRIDE_FILENAME = ".sonar-triage.json"
REQUEST_TIMEOUT_SECONDS = 30


def load_rules(rules_path=DEFAULT_RULES_PATH):
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    preserved = dict(data.get("preserved_rules", {}))
    conditional = dict(data.get("conditional_rules", {}))
    actionable = dict(data.get("actionable_rules", {}))

    # Merge optional repo-local overrides if present in cwd or parent directories
    cur = Path.cwd()
    for _ in range(5):
        local_override = cur / LOCAL_OVERRIDE_FILENAME
        if local_override.exists():
            with open(local_override, "r", encoding="utf-8") as f:
                local_data = json.load(f)
            preserved.update(local_data.get("preserved_rules", {}))
            conditional.update(local_data.get("conditional_rules", {}))
            actionable.update(local_data.get("actionable_rules", {}))
            break
        if cur.parent == cur:
            break
        cur = cur.parent

    return preserved, conditional, actionable


def load_env_file(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    return env


def normalize_config(raw):
    cfg = {}
    host = raw.get("SONARQUBE_HOST_URL") or raw.get("sonar.host.url")
    project = raw.get("SONARQUBE_PROJECT_KEY") or raw.get("sonar.projectKey")
    token = (
        raw.get("SONARQUBE_TOKEN")
        or raw.get("SONAR_TOKEN")
        or raw.get("sonar.token")
        or raw.get("sonar.login")
    )
    if host:
        cfg["SONARQUBE_HOST_URL"] = host
    if project:
        cfg["SONARQUBE_PROJECT_KEY"] = project
    if token:
        cfg["SONARQUBE_TOKEN"] = token
    return cfg


def discover_config():
    merged = {}
    cur = Path.cwd()
    for _ in range(5):
        # Merge in priority order so missing keys (e.g. token) fall back to later files
        for candidate_name in [".env", "mvn.env", "sonar-project.properties"]:
            candidate = cur / candidate_name
            if candidate.exists():
                normalized = normalize_config(load_env_file(candidate))
                for k, v in normalized.items():
                    merged.setdefault(k, v)
        if cur.parent == cur:
            break
        cur = cur.parent
    return merged


def _request_issues_page(base_url, headers, project_key, statuses, page_size, page, status_param):
    params = {
        "componentKeys": project_key,
        status_param: statuses,
        "ps": str(page_size),
        "p": str(page),
        "s": "FILE_LINE",
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_issues(host_url, project_key, token, statuses="OPEN,CONFIRMED"):
    base_url = host_url.rstrip("/") + "/api/issues/search"
    page = 1
    page_size = 100
    all_issues = []
    status_param = "issueStatuses"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Sonar-Triage-Agent/1.0",
    }
    if token:
        # SonarQube uses HTTP Basic Auth with token as username and empty password
        auth_str = base64.b64encode(f"{token}:".encode()).decode()
        headers["Authorization"] = f"Basic {auth_str}"

    while True:
        try:
            data = _request_issues_page(
                base_url, headers, project_key, statuses, page_size, page, status_param
            )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            # SonarQube 9.x LTS and SonarCloud use `statuses` instead of `issueStatuses`
            if e.code == 400 and status_param == "issueStatuses":
                status_param = "statuses"
                try:
                    data = _request_issues_page(
                        base_url, headers, project_key, statuses, page_size, page, status_param
                    )
                except urllib.error.HTTPError as retry_err:
                    retry_body = retry_err.read().decode("utf-8", errors="replace")
                    sys.stderr.write(f"HTTP Error {retry_err.code}: {retry_err.reason}\n")
                    sys.stderr.write(f"Response: {retry_body}\n")
                    sys.exit(1)
            else:
                sys.stderr.write(f"HTTP Error {e.code}: {e.reason}\n")
                sys.stderr.write(f"Response: {error_body}\n")
                sys.exit(1)
        except urllib.error.URLError as e:
            sys.stderr.write(f"Network error: {e.reason}\n")
            sys.exit(1)

        issues = data.get("issues", [])
        all_issues.extend(issues)

        total = data.get("total", 0)
        if len(all_issues) >= total or not issues:
            break

        page += 1

    return all_issues


def categorize_issues(issues, preserved_rules, conditional_rules, actionable_rules):
    actionable = []
    ignored = []
    conditional = []
    unclassified = []

    for issue in issues:
        rule = issue.get("rule", "")
        component = issue.get("component", "")
        line = issue.get("line", 0)
        message = issue.get("message", "")
        key = issue.get("key", "")
        severity = issue.get("severity", "")

        file_path = component.split(":", 1)[-1] if ":" in component else component

        item = {
            "key": key,
            "rule": rule,
            "file": file_path,
            "line": line,
            "message": message,
            "severity": severity,
        }

        if rule in preserved_rules:
            item["reason"] = preserved_rules[rule]["reason"]
            ignored.append(item)
        elif rule in conditional_rules:
            item["condition"] = conditional_rules[rule]["condition"]
            conditional.append(item)
        elif rule in actionable_rules:
            item["guidance"] = actionable_rules[rule]
            actionable.append(item)
        else:
            unclassified.append(item)

    return actionable, ignored, conditional, unclassified


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and triage SonarQube issues for Java and Spring Boot projects."
    )
    parser.add_argument("--url", help="SonarQube host URL")
    parser.add_argument("--project", help="SonarQube project key")
    parser.add_argument("--token", help="SonarQube authentication token")
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "summary"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--actionable-only", action="store_true", help="Output only actionable issues"
    )

    args = parser.parse_args()

    preserved_rules, conditional_rules, actionable_rules = load_rules()
    cfg = discover_config()
    host_url = args.url or os.environ.get("SONARQUBE_HOST_URL") or cfg.get("SONARQUBE_HOST_URL")
    project_key = (
        args.project
        or os.environ.get("SONARQUBE_PROJECT_KEY")
        or cfg.get("SONARQUBE_PROJECT_KEY")
    )
    token = (
        args.token
        or os.environ.get("SONARQUBE_TOKEN")
        or os.environ.get("SONAR_TOKEN")
        or cfg.get("SONARQUBE_TOKEN")
    )

    if not host_url or not project_key:
        sys.stderr.write(
            "Error: SONARQUBE_HOST_URL and SONARQUBE_PROJECT_KEY must be provided via CLI, environment, or config file.\n"
        )
        sys.exit(1)

    issues = fetch_issues(host_url, project_key, token)
    actionable, ignored, conditional, unclassified = categorize_issues(
        issues, preserved_rules, conditional_rules, actionable_rules
    )

    if args.format == "json":
        out = {
            "total": len(issues),
            "actionable_count": len(actionable),
            "ignored_count": len(ignored),
            "conditional_count": len(conditional),
            "unclassified_count": len(unclassified),
            "actionable": actionable,
        }
        if not args.actionable_only:
            out["ignored"] = ignored
            out["conditional"] = conditional
            out["unclassified"] = unclassified
        print(json.dumps(out, indent=2))
        return

    if args.format == "summary":
        print(f"Total issues: {len(issues)}")
        print(f"Actionable issues: {len(actionable)}")
        print(f"Ignored (Preserved Patterns): {len(ignored)}")
        print(f"Conditional (Context-Dependent): {len(conditional)}")
        print(f"Unclassified: {len(unclassified)}")
        return

    # Markdown format
    print(f"# SonarQube Triage Report for {project_key}")
    print(f"\n- **Total Open/Confirmed Issues**: {len(issues)}")
    print(f"- **Actionable Issues**: {len(actionable)}")
    print(f"- **Preserved Patterns**: {len(ignored)}")
    print(f"- **Conditional (Context-Dependent)**: {len(conditional)}")
    print(f"- **Unclassified Issues**: {len(unclassified)}\n")

    print("## 1. Actionable Issues (Safe & Recommended to Fix)\n")
    if not actionable:
        print("No actionable issues found! 🎉\n")
    else:
        print("| Rule | Location | Severity | Message | Guidance |")
        print("|---|---|---|---|---|")
        for item in actionable:
            loc = f"`{item['file']}:{item['line']}`"
            print(
                f"| `{item['rule']}` | {loc} | {item['severity']} | {item['message']} | {item['guidance']} |"
            )
        print()

    if not args.actionable_only:
        if conditional:
            print("## 2. Conditional Issues (Verify Context Before Fixing or Preserving)\n")
            print("| Rule | Location | Severity | Message | Condition |")
            print("|---|---|---|---|---|")
            for item in conditional:
                loc = f"`{item['file']}:{item['line']}`"
                print(
                    f"| `{item['rule']}` | {loc} | {item['severity']} | {item['message']} | {item['condition']} |"
                )
            print()

        print("## 3. Preserved Patterns (DO NOT TOUCH - Established Framework Patterns)\n")
        if not ignored:
            print("No preserved pattern issues found.\n")
        else:
            print("| Rule | Location | Message | Rationale |")
            print("|---|---|---|---|")
            for item in ignored:
                loc = f"`{item['file']}:{item['line']}`"
                print(
                    f"| `{item['rule']}` | {loc} | {item['message']} | {item['reason']} |"
                )
            print()

        if unclassified:
            print("## 4. Unclassified Issues (Requires Manual Assessment)\n")
            print("| Rule | Location | Severity | Message |")
            print("|---|---|---|---|")
            for item in unclassified:
                loc = f"`{item['file']}:{item['line']}`"
                print(f"| `{item['rule']}` | {loc} | {item['severity']} | {item['message']} |")
            print()


if __name__ == "__main__":
    main()
