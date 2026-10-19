# Changelog

All notable changes to GSD for Antigravity are documented in this file.

## [1.6.0] - 2026-10-19

### Added
- GSD framework workflows, skills, templates, and subagent definitions
- Cross-platform PowerShell and Bash script validation suite
- Fast repository search utility scripts (`search_repo.ps1` and `search_repo.sh`)
- Pre-milestone archiving for decisions and journal entries

### Fixed
- Execution flow requires phase goal verification before marking completion
- Scoped variable parsing in PowerShell scripts and workflow commands
- Parenthesized `Test-Path` logic joins in project and codebase scanners
- Ripgrep and grep argument parsing for positional paths and options in `search_repo.sh`
- Planning lock strict regex validation for `Status: FINALIZED`
- Planner context loading includes `DECISIONS.md` from phase discussions
- Conditional staging of optional `REQUIREMENTS.md` during phase completion
- Required input files and directory validation across all validator scripts

## [1.2.0] - 2026-01-17

### Added
- Cross-platform support with Bash equivalents for all workflows
- `/web-search` workflow for external technical research
- Dual-syntax quick reference documentation
