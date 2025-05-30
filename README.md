# git‑sync

A lightweight, extensible CLI tool to automate the distribution and synchronization of GitHub Actions workflows across multiple repositories. Inspired by GitOps, Helm-style templating, and modular CI/CD practices, `git-pilot` uses Jinja2 templates and a single configuration file to manage workflow updates, cleanup, and preview.

---

## 🚀 Key Features

- **Multi‑Repository Sync**: Apply one or more workflow templates to any number of repositories with a single command.
- **Helm‑Style Templating**: Supports `.tpl` macros, includes, and dynamic variable injection.
- **Per‑Repository Overrides**: Customize branches, commit messages, paths, variables, and template selection per repository.
- **Regex‑Driven Template Selection**: Use patterns to precisely control which templates apply to which repositories.
- **Interactive Change Preview**: Before applying changes, see a side-by-side comparison of created, updated, and deleted files with toggles and highlights.
- **State Management**: Tracks previously synced workflows and automatically cleans up obsolete files.
- **Extensible Provider Model**: Built-in support for GitHub, with support for other platforms planned.

---

## 📦 Installation

Install the tool using pip:

```bash
pip install git-pilot
```

---

## Usage

Initialize a new template structure: Creates a starter template directory (test/) with example templates, partials, and a values.yml file. Useful for bootstrapping a new setup.

```bash
git-pilot init --template-dir test
```

Run synchronization across configured repositories: Renders templates with variables, compares with the current state in each repository, and shows an interactive preview of changes. Applies updates only after confirmation.

```bash
git-pilot sync \
  --token <your-github-token> \
  --templates test \
  --values test/values.yml
```

### Options:

| Flag          | Description                            |
| ------------- | -------------------------------------- |
| `--token`     | GitHub Personal Access Token           |
| `--templates` | Path to the root template directory    |
| `--values`    | Path to the config file (`values.yml`) |

---

## 🧩 Configuration (`values.yml`)

The configuration file defines global defaults and per-repo overrides for:

* Branch name
* Commit message
* Target directory for rendered templates
* Regex patterns for template selection
* Variables to inject into templates

See the [Configuration Reference](docs/configuration.md) for a detailed breakdown.

---

## 🧠 Templating

`git-pilot` supports Helm-style rendering using Jinja2, including:

* Custom delimiters to avoid conflicts with GitHub Actions syntax
* Shared macro files and reusable partial templates
* Built-in helper functions like `indent`, `to_yaml`, `tpl()`, etc.

See the [Templating Guide](docs/templating.md) for structure and usage examples.

---

## 💾 State Management

A local JSON state file tracks:

* Which templates were applied to which repositories and branches
* SHA of the rendered content to detect changes
* Obsolete workflows to remove when templates are no longer matched

This ensures safe, idempotent operations and automatic cleanup.

---

## 🧪 Interactive Comparison Viewer

Before applying changes, `git-pilot` presents a full summary:

* **Created**: New files to be added
* **Updated**: Modified files with side-by-side diffs
* **Deleted**: Stale or obsolete files to be removed

You can visually inspect changes before confirming. Nothing is pushed until confirmed.

---

## 🤝 Contributing

We welcome contributions! To get started:

1. Create a virtual environment and install dev dependencies.
2. Run the test suite and linters.
3. Implement your feature or fix.
4. Submit a pull request with a clear description.

See the [Technical Architecture Guide](docs/architecture-guide) for details.

---