# git-pilot

> Sync workflows, configs, and more across 10+ repos in seconds using Helm-style templates.

---

[![GitHub stars](https://img.shields.io/github/stars/r3d-shadow/git-pilot?style=social)](https://github.com/r3d-shadow/git-pilot/stargazers)
[![PyPI version](https://img.shields.io/pypi/v/git-pilot)](https://pypi.org/project/git-pilot/)
[![License](https://img.shields.io/github/license/r3d-shadow/git-pilot)](LICENSE)

---

## 🚀 Why Git-Pilot?

Managing configuration and CI/CD files across 10, 20, or 100+ repositories is a nightmare.

**`git-pilot` is your autopilot for repository file sync.** It brings GitOps discipline, Helm-style templating, and one-command sync to modern DevOps pipelines.

### 🧠 Built for DevEx

* **One command to sync them all:** Apply templates to any number of GitHub repos in one go.
* **Helm-style power:** Use partials, macros (`.tpl`), and regex-driven rendering logic.
* **Preview before you push:** Interactive side-by-side diffs before anything is committed.
* **State-aware syncs:** Tracks changes and removes stale files automatically.
* **Per-repo flexibility:** Custom branches, commit messages, and variable overrides.

---

## 🧰 What It Does

| Feature                    | Description                                                                   |
| -------------------------- | ----------------------------------------------------------------------------- |
| 🔁 Multi-Repo Sync         | Render and push files across 1 or 100 repos with a single command             |
| 🧩 Helm-Style Templates    | Use Jinja2 with custom delimiters, includes, and reusable `.tpl` macros       |
| 🔍 Interactive Diff Viewer | See what changes before you commit—created, updated, deleted files preview    |
| 🧬 Per-Repo Customization  | Branches, paths, commit messages, and injected variables                      |
| 🧹 Auto-Cleanup            | Deletes stale files intelligently based on diff and state tracking            |
| 🌐 GitHub Native (for now) | Built-in support for GitHub with extensible architecture for future providers |

---

## 📦 Installation

```bash
pip install git-pilot
```

---

## ✨ Getting Started: First Sync in 5 Minutes

### 1. Initialize Template Directory

```bash
git-pilot init --template-dir my-templates
```

This creates a sample structure with:

* Example templates (`*.yml.j2`)
* Partials in `includes/`
* Helper macros in `_helpers.tpl`
* A working `values.yml` config

---

### 2. Customize Templates and Values

Edit `my-templates/values.yml`:

```yaml
defaults:
  branch: main
  message: "git-pilot: update workflows"
  path: ".github/workflows"
  vars:
    ci_name: my-pipeline
    env: dev
  templates:
    - ".*\.j2$"

repos:
  - name: r3d-shadow/git-pilot-test-1
    vars:
      job_id: scan1
  - name: r3d-shadow/git-pilot-test-2
    branch: main # override
    vars:
      job_id: scan2
      env: prod # override
```

---

### 3. Run Your First Sync

```bash
cd my-templates

git-pilot sync \
  --token $GITHUB_TOKEN \
  --templates ./ \
  --values ./values.yml
```

✅ You’ll see a full visual diff. Confirm to sync. That’s it!

![Demo GIF](https://github.com/r3d-shadow/git-pilot/blob/main/docs/assets/demo.gif)

---

## 📘 Docs

* [Templating Guide](https://github.com/r3d-shadow/git-pilot/blob/main/docs/templating.md) — Includes, macros, helpers, and Jinja2 syntax
* [Configuration Reference](https://github.com/r3d-shadow/git-pilot/blob/main/docs/configuration.md) — All config options and repo overrides
* [Architecture Guide](https://github.com/r3d-shadow/git-pilot/blob/main/docs/architecture-guide.md) — Extending providers and internal design
* [Contributing to `git-pilot`](https://github.com/r3d-shadow/git-pilot/blob/main/docs/contributing.md)
* [Roadmap](https://github.com/r3d-shadow/git-pilot/blob/main/docs/roadmap.md)

---

## 🛠️ Advanced Examples

* Sync GitHub Actions, README.md, configs, policies, and more
* Regex-targeted templates per repo
* Environments like `dev`, `staging`, `prod`
* Centralized secrets and configurations with overrides

→ See `/example-template-dir` for ready-to-copy setups

---

## 🤝 Contributing

We welcome contributors! Here's how to get started:

```
git clone https://github.com/r3d-shadow/git-pilot.git
cd git-pilot
python3 -m venv venv
source venv/bin/activate
pip install -e .
git-pilot
```

Open a PR with a clear description. See the [Architecture Guide](https://github.com/r3d-shadow/git-pilot/blob/main/docs/architecture-guide.md) for more details.

---

## 🚀 Spread the Word

> Just found this tool called `git-pilot` — sync your GitHub Actions, configs, and more across 10+ repos with a single command. Helm-style templates. Pure 🔥.

Tweet it. Star it. Fork it. Contribute.

Let’s build better DevOps pipelines together.

---

## 🪪 License

Apache-2.0 license — [LICENSE](https://github.com/r3d-shadow/git-pilot/blob/main/LICENSE)


