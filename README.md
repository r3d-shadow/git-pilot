# ci‑sync

A lightweight, extensible CLI tool to automate the distribution and synchronization of GitHub Actions workflows across multiple repositories. Inspired by GitOps, Helm-style templating, and modular CI/CD practices, ci‑sync uses Jinja2 templates and a single configuration file to manage workflow updates, cleanup, and preview.

## Overview

ci‑sync centralizes CI/CD pipeline management by allowing organizations to define reusable workflow templates in one place and apply them to any set of repositories. It tracks previous deployments, offers dry‑run previews with interactive diffs, and automatically removes obsolete workflow files.

## Key Features

* **Multi‑Repository Sync**: Apply one or more workflow templates to any number of repositories with a single command.
* **Helm‑Style Jinja2 Templating**: Render dynamic workflows using structured templates, shared partials, and helper macros. Supports `.tpl` files for reusable logic.
* **Per‑Repository Overrides**: Customize branch targets, commit messages, file paths, template variables, and template patterns for each repository.
* **Regex‑Driven Template Selection**: Use glob or regex patterns to control which templates apply to which repos.
* **Interactive Dry‑Run with Diffs**: Preview and toggle exact changes in each file before committing, with keyboard navigation and diff panels.
* **State Management**: Persist a local state file to track previously synced files and remove renamed or obsolete workflows automatically.
* **Extensible Provider Model**: Built around a provider abstraction, currently supports GitHub with the ability to add GitLab, Azure DevOps, or other platforms.

## Getting Started

1. **Installation**

   * Install via pip or clone the repository
   * Ensure dependencies for Jinja2, PyYAML, PyGithub, Rich are available

2. **Directory Layout**

   * **templates/**: Jinja2 template files with support for Helm-style layout and `.tpl` helpers
   * **includes/**: Shared macro files and template functions
   * **core/**: Loader, comparator, diff and state management modules
   * **providers/**: API integrations (e.g. GitHub)
   * **cli.py**: Main command‑line interface
   * **values.yml**: Configuration file defining defaults and per‑repo settings

3. **Configuration**

   * Define global defaults for branch, file path, commit message, template patterns, and variables.
   * List repositories with optional overrides for any of those settings and include custom variables.

4. **Usage**

   * Run the CLI with parameters for access token, template directory, values file, and optional dry‑run.
   * Use interactive diff viewer to toggle and inspect changes.
   * Commit changes by omitting dry‑run.

## Configuration File (`values.yml`)

* **defaults**: Global settings applied to all repositories.
* **repos**: A list or map of repository entries, each with a name and any overrides.
* **templates**: Regex patterns controlling which template files get rendered for each repo.
* **vars**: Key‑value pairs passed into the templates for dynamic substitution.

## Templating

* Uses Helm-style Jinja2 rendering engine.
* Templates live under a central directory and may include shared partials or `.tpl` helper macros.
* Custom delimiters (`[[ ... ]]`, `[% ... %]`) avoid conflicts with GitHub Actions syntax.
* Supports reusable functions like `indent`, `to_yaml`, etc. through globally injected macros.

## State Management

* A local JSON state file records the last synced path and SHA for each template in each repository.
* When a template or path changes, ci‑sync will remove the obsolete workflow file before applying the new one.
* State updates are atomic, ensuring consistency across runs.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository and clone locally.
2. Run the test suite and ensure linters pass.
3. Implement new features or fixes, following existing code style.
4. Submit a pull request with a clear description of changes.