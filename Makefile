.DEFAULT_GOAL := help

.PHONY: help install validate test status uninstall new clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all personal and vendor skills to all agents (symlink mode)
	@./scripts/install.sh --agent all --mode symlink

install-personal: ## Install only personal skills (skip vendor)
	@./scripts/install.sh --agent all --mode symlink --no-vendor

update-vendor: ## Pull latest upstream commits for vendor submodules
	@git submodule update --remote --merge

install-claude: ## Install skills to Claude Code
	@./scripts/install.sh --agent claude --mode symlink

install-antigravity: ## Install skills to Google Antigravity
	@./scripts/install.sh --agent antigravity --mode symlink

install-opencode: ## Install skills to OpenCode
	@./scripts/install.sh --agent opencode --mode symlink

install-codex: ## Install skills to OpenAI Codex
	@./scripts/install.sh --agent codex --mode symlink

install-cursor: ## Install skills to Cursor
	@./scripts/install.sh --agent cursor --mode symlink

status: ## Show installation status across all agents
	@./scripts/install.sh --status

uninstall: ## Remove installed skills from all agents
	@./scripts/install.sh --uninstall

validate: ## Validate and lint all skills against open standards
	@./scripts/validate.sh

test: validate ## Alias for validate

fix: ## Auto-generate missing wrappers and fix script permissions
	@./scripts/validate.py --fix

new: ## Scaffold a new skill (usage: make new NAME=my-skill [DESC="..."])
	@./scripts/new-skill.sh "$(NAME)" "$(DESC)"

clean: ## Clean up any temporary files
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
