# 📘 Configuration Reference

The `values.yml` file powers the behavior of `git-pilot sync`, defining how templates are applied across multiple repositories. This document outlines the structure and options available.

---

## 🧾 File Structure

```yaml
defaults:
  branch: main
  path: .github/workflows
  message: "ci-sync: update workflows"
  templates:
    - ".*\.yml\.j2"
  vars:
    global_var: "value"

repos:
  - name: org/repo-name
    branch: dev
    message: "ci: update workflows"
    path: .github/workflows/custom
    templates:
      - "example.*\.yml\.j2"
    vars:
      project: my-service
      environment: dev
```

---

## 🔧 `defaults`

Defines global defaults applied to all repositories unless overridden.

| Key         | Description                                 |
| ----------- | ------------------------------------------- |
| `branch`    | Default branch to commit changes to         |
| `path`      | Default directory where rendered files go   |
| `message`   | Default commit message                      |
| `templates` | Regex patterns to match templates to render |
| `vars`      | Key-value pairs injected into all templates |

---

## 📦 `repos`

List of target repositories with optional overrides for defaults.

Each entry supports:

| Key         | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `name`      | Repository name in the form `owner/repo`                      |
| `branch`    | Branch to commit to (overrides `defaults.branch`)             |
| `message`   | Commit message (overrides `defaults.message`)                 |
| `path`      | Output directory (overrides `defaults.path`)                  |
| `templates` | Regex patterns for selecting templates for this repo          |
| `vars`      | Variables injected into templates (merged with global `vars`) |

---

## ✅ Example Minimal Config

```yaml
defaults:
  branch: main
  path: .github/workflows
  templates:
    - ".*\.yml\.j2"

repos:
  - name: my-org/app-api
    vars:
      app_name: api
      env: prod
```
