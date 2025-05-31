# 📘 Configuration Reference

The `values.yml` file defines how templates are rendered and synced to multiple repositories using `git-pilot sync`. It supports a mix of global defaults and per-repo overrides to control branches, file paths, templates, variables, and commit messages.

Use this config to sync **any type of file** — including GitHub Actions workflows, README.md, policies, Terraform modules, or any custom configuration — across dozens or hundreds of repositories.

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

These values apply to **all repositories** unless explicitly overridden in the `repos:` section. They're useful for DRY (Don't Repeat Yourself) configs.

| Key         | Type       | Description                                                               |
| ----------- | ---------- | ------------------------------------------------------------------------- |
| `branch`    | string     | Default branch to push changes to                                         |
| `path`      | string     | Target directory inside each repo where rendered files will be written    |
| `message`   | string     | Default commit message for pushes                                         |
| `templates` | list       | Regex patterns matching templates to render (relative to template root)   |
| `vars`      | dictionary | Global variables injected into all templates (can be overridden per repo) |

---

## 📦 `repos`

A list of individual repositories where templates will be rendered and committed.

Each entry supports all fields in `defaults`, allowing per-repo overrides:

| Key         | Type       | Description                                                 |
| ----------- | ---------- | ----------------------------------------------------------- |
| `name`      | string     | GitHub repository in the format `owner/repo`                |
| `branch`    | string     | Branch to commit to (overrides `defaults.branch`)           |
| `message`   | string     | Custom commit message (overrides `defaults.message`)        |
| `path`      | string     | Output path for rendered files (overrides `defaults.path`)  |
| `templates` | list       | Regex patterns to match which templates apply to this repo  |
| `vars`      | dictionary | Variables scoped to this repo (merged with `defaults.vars`) |

Notes:

* `templates` is evaluated as a regex; you can target specific files for specific repos.
* `vars` from `defaults` and `repos[n]` are merged; repo-specific values override global ones.

---

## 🔍 Template Matching Logic

Templates are matched using the regex patterns defined in `templates:`. This supports advanced targeting:

* `.*\.j2$`: Apply all `.j2` templates
* `example-.*\.yml\.j2`: Apply only files that start with `example-`
* `.*\/prod\/.*\.j2$`: Apply only templates within a `prod/` folder

The template path is always relative to the root passed to `--templates`.

---

## 🧠 Variable Injection

Templates are rendered using Jinja2, and can access all keys under `vars`. Variable priority:

1. Repo-specific `vars`
2. Global `defaults.vars`
3. Built-in variables (like `repo_name`, `repo_owner` in future releases)

Example usage in a template:

```jinja
name: [[ app_name ]]
environment: [[ env ]]
```

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

This will render and sync all `*.yml.j2` templates to `.github/workflows` in `my-org/app-api`, injecting `app_name` and `env` into the template context.

---

## 🛠️ Tips

* You can sync more than workflows: any file type like `README.md`, `.yamllint`, or `CODEOWNERS` is supported.
* Avoid hardcoding repo-specific values in templates — use `vars` and keep templates reusable.
* Use multiple regex patterns in `templates:` to apply different templates to different repos.
* Combine with conditionals in templates for max flexibility (Jinja2)