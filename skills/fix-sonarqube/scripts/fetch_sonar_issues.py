#!/usr/bin/env python3
"""
Fetch and triage SonarQube issues for Java and Spring Boot projects.
Categorizes issues into actionable fixes vs preserved framework patterns.
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

# Rules that MUST be preserved because they represent standard architectural patterns
IGNORED_RULES = {
    "java:S3252": {
        "name": "Static member accessed via subclass",
        "reason": "MapStruct and annotation processors often require static entity constants to be referenced via the target concrete entity class (e.g. Entity.ATTR_ID), not the base interface.",
        "action": "PRESERVE",
    },
    "java:S119": {
        "name": "Type parameter name convention",
        "reason": "Core generic architectural type parameters (e.g. <T extends BaseEntity<T>>, <ID, E>) are intentional framework API contracts.",
        "action": "PRESERVE",
    },
    "java:S1135": {
        "name": "TODO tag tracking",
        "reason": "TODO comments must be resolved by genuine implementation, never deleted merely to satisfy SonarQube.",
        "action": "PRESERVE",
    },
    "xml:S1135": {
        "name": "XML TODO tag tracking",
        "reason": "TODO comments in XML must be addressed by implementation, never deleted.",
        "action": "PRESERVE",
    },
    "java:S1874": {
        "name": "Deprecated code usage",
        "reason": "@Deprecated methods and classes are intentionally maintained for backward compatibility until major release milestones.",
        "action": "PRESERVE",
    },
    "java:S1123": {
        "name": "Deprecated tag without javadoc",
        "reason": "Deprecation tags are maintained intentionally for API contract tracking.",
        "action": "PRESERVE",
    },
    "java:S1602": {
        "name": "Lambda expression block braces",
        "reason": "In multi-overloaded functional interfaces, explicit braces `{ return ...; }` disambiguate overloaded functional signatures (e.g., Supplier vs Consumer). Removing braces breaks compilation.",
        "action": "PRESERVE",
    },
    "java:S3011": {
        "name": "Reflection accessibility bypass",
        "reason": "Base models or dynamic reflection utilities require accessible field modification for generic copying/serialization.",
        "action": "PRESERVE",
    },
    "java:S2160": {
        "name": "Subclass equals override",
        "reason": "Subclasses extending a reflection-based or base model rely on base equals/hashCode and should not define redundant boilerplate overrides.",
        "action": "PRESERVE",
    },
    "java:S6548": {
        "name": "Singleton pattern",
        "reason": "Framework constants and fallback singleton instances use singleton patterns intentionally.",
        "action": "PRESERVE",
    },
    "java:S106": {
        "name": "Standard output usage",
        "reason": "CLI utilities and standalone migration scripts intentionally print to stdout/stderr.",
        "action": "PRESERVE",
    },
}

# Rules that are high-priority candidates for cleanup
ACTIONABLE_RULES = {
    "java:S1068": "Unused private field - safe to remove.",
    "java:S1481": "Unused local variable - safe to remove.",
    "java:S1144": "Unused private method - safe to remove.",
    "java:S1488": "Immediately returned local variable - inline directly into return statement.",
    "java:S3776": "Cognitive Complexity - refactor deeply nested conditionals into guard clauses or helper methods.",
    "java:S2142": "InterruptedException handling - call Thread.currentThread().interrupt() before throwing wrapper exception.",
    "java:S5164": "ThreadLocal cleanup - call ThreadLocal.remove() in a finally block to prevent memory leaks.",
    "java:S1161": "Missing @Override annotation - add @Override to clarify interface implementation.",
    "java:S1155": "Collection.isEmpty() - replace size() == 0 or size() > 0 with isEmpty() or !isEmpty().",
    "java:S2129": "Boxed constructor - replace new Long()/new String() with literals or .valueOf().",
    "java:S1128": "Unused import - remove redundant import statement.",
    "java:S1192": "String literal duplicated - extract common constant for repeated strings.",
    "java:S2259": "Potential NullPointerException - add null guard or Objects.requireNonNull.",
    "java:S125": "Commented-out code - remove dead commented code blocks.",
    "java:S1186": "Empty method - add explanatory comment or implementation.",
    "java:S1172": "Unused method parameter - check if signature is bound by polymorphic contract before modifying.",
    "java:S112": "Generic exceptions - evaluate whether to throw domain-specific exception or if framework wrapper is expected.",
}


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


def discover_config():
    cur = Path.cwd()
    for _ in range(5):
        for candidate_name in [".env", "mvn.env", "sonar-project.properties"]:
            candidate = cur / candidate_name
            if candidate.exists():
                return load_env_file(candidate)
        cur = cur.parent
    return {}


def fetch_issues(host_url, project_key, token, statuses="OPEN,CONFIRMED"):
    base_url = host_url.rstrip("/") + "/api/issues/search"
    page = 1
    page_size = 100
    all_issues = []

    headers = {
        "Accept": "application/json",
        "User-Agent": "Sonar-Triage-Agent/1.0",
    }
    if token:
        # SonarQube uses HTTP Basic Auth with token as username and empty password
        auth_str = base64.b64encode(f"{token}:".encode()).decode()
        headers["Authorization"] = f"Basic {auth_str}"

    while True:
        params = {
            "componentKeys": project_key,
            "issueStatuses": statuses,
            "ps": str(page_size),
            "p": str(page),
            "s": "FILE_LINE",
        }
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"HTTP Error {e.code}: {e.reason}\n")
            error_body = e.read().decode("utf-8", errors="replace")
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


def categorize_issues(issues):
    actionable = []
    ignored = []
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

        if rule in IGNORED_RULES:
            item["reason"] = IGNORED_RULES[rule]["reason"]
            ignored.append(item)
        elif rule in ACTIONABLE_RULES:
            item["guidance"] = ACTIONABLE_RULES[rule]
            actionable.append(item)
        else:
            unclassified.append(item)

    return actionable, ignored, unclassified


def main():
    parser = argparse.ArgumentParser(description="Fetch and triage SonarQube issues for Java and Spring Boot projects.")
    parser.add_argument("--url", help="SonarQube host URL")
    parser.add_argument("--project", help="SonarQube project key")
    parser.add_argument("--token", help="SonarQube authentication token")
    parser.add_argument("--format", choices=["markdown", "json", "summary"], default="markdown", help="Output format")
    parser.add_argument("--actionable-only", action="store_true", help="Output only actionable issues")

    args = parser.parse_args()

    cfg = discover_config()
    host_url = args.url or os.environ.get("SONARQUBE_HOST_URL") or cfg.get("SONARQUBE_HOST_URL")
    project_key = args.project or os.environ.get("SONARQUBE_PROJECT_KEY") or cfg.get("SONARQUBE_PROJECT_KEY")
    token = args.token or os.environ.get("SONARQUBE_TOKEN") or cfg.get("SONARQUBE_TOKEN")

    if not host_url or not project_key:
        sys.stderr.write("Error: SONARQUBE_HOST_URL and SONARQUBE_PROJECT_KEY must be provided via CLI, environment, or env file.\n")
        sys.exit(1)

    issues = fetch_issues(host_url, project_key, token)
    actionable, ignored, unclassified = categorize_issues(issues)

    if args.format == "json":
        out = {
            "total": len(issues),
            "actionable_count": len(actionable),
            "ignored_count": len(ignored),
            "unclassified_count": len(unclassified),
            "actionable": actionable,
        }
        if not args.actionable_only:
            out["ignored"] = ignored
            out["unclassified"] = unclassified
        print(json.dumps(out, indent=2))
        return

    if args.format == "summary":
        print(f"Total issues: {len(issues)}")
        print(f"Actionable issues: {len(actionable)}")
        print(f"Ignored (Framework Patterns): {len(ignored)}")
        print(f"Unclassified: {len(unclassified)}")
        return

    # Markdown format
    print(f"# SonarQube Triage Report for {project_key}")
    print(f"\n- **Total Open/Confirmed Issues**: {len(issues)}")
    print(f"- **Actionable Issues**: {len(actionable)}")
    print(f"- **Preserved Framework Patterns**: {len(ignored)}")
    print(f"- **Unclassified Issues**: {len(unclassified)}\n")

    print("## 1. Actionable Issues (Safe & Recommended to Fix)\n")
    if not actionable:
        print("No actionable issues found! 🎉\n")
    else:
        print("| Rule | Location | Severity | Message | Guidance |")
        print("|---|---|---|---|---|")
        for item in actionable:
            loc = f"`{item['file']}:{item['line']}`"
            print(f"| `{item['rule']}` | {loc} | {item['severity']} | {item['message']} | {item['guidance']} |")
        print()

    if not args.actionable_only:
        print("## 2. Preserved Patterns (DO NOT TOUCH - Established Framework Patterns)\n")
        if not ignored:
            print("No preserved pattern issues found.\n")
        else:
            print("| Rule | Location | Message | Rationale |")
            print("|---|---|---|---|")
            for item in ignored:
                loc = f"`{item['file']}:{item['line']}`"
                print(f"| `{item['rule']}` | {loc} | {item['message']} | {item['reason']} |")
            print()

        if unclassified:
            print("## 3. Unclassified Issues (Requires Manual Assessment)\n")
            print("| Rule | Location | Severity | Message |")
            print("|---|---|---|---|")
            for item in unclassified:
                loc = f"`{item['file']}:{item['line']}`"
                print(f"| `{item['rule']}` | {loc} | {item['severity']} | {item['message']} |")
            print()


if __name__ == "__main__":
    main()
