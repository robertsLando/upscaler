# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Shared Instructions

Development guidelines, architecture details, coding standards, and contribution patterns are maintained in a single shared location:

- **[`.github/copilot-instructions.md`](.github/copilot-instructions.md)** — primary reference for project conventions, architecture, testing strategy, and workflows.

Please read that file first. It is the source of truth and applies to all AI-assisted development tools, including Claude Code.

## Quick Reference

```bash
make install   # Install dependencies with uv
make run       # Start the FastAPI application
make test      # Run test suite
make lint      # Check code with ruff and prettier
make format    # Auto-format code
make clean     # Remove cache and temporary files
```
