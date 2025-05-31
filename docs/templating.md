# 🧠 Templating Guide

`git-pilot` uses a **Helm-style templating engine** built on **Jinja2** to render GitHub Actions workflows (or any text-based config files). This guide covers templating concepts, syntax, helpers, best practices, and an end-to-end example.

---

## 🧱 Template Files

* Templates are **Jinja2** files with a `.j2` suffix.
* Organize templates logically for maintainability:

  * **Templates**: Full files rendered as output (e.g. `example.yml.j2`)
  * **Includes**: Reusable partial snippets (e.g. `includes/units/*.j2`)
  * **Helpers**: Macro files ending in `.tpl` containing reusable functions/macros (e.g. `_helpers.tpl`)

---

## 🔀 Custom Delimiters

`git-pilot` uses custom delimiters to avoid conflicts with GitHub Actions YAML syntax:

| Purpose           | Syntax                               |
| ----------------- | ------------------------------------ |
| Variables         | `[[ variable_name ]]`                |
| Statements/Blocks | `[% if condition %] ... [% endif %]` |

> These custom delimiters let you write Jinja2 logic without clashing with `${{ }}` or YAML syntax in workflows.

---

## ⚙️ Built-in Template Functions & Helpers

You can use any Jinja2 feature plus these global helpers:

| Function        | Description                                          |
| --------------- | ---------------------------------------------------- |
| `indent(n, s)`  | Indent multiline string `s` by `n` spaces            |
| `capitalize(s)` | Capitalize first letter of string `s`                |

---

## 📥 Includes and Macros

Modularize templates by breaking them into smaller parts.

### Example Include File

```jinja
# templates/includes/units/hello-world.j2
name: hello-world
run: echo "Hello [[ name ]]!"
```

### Include Usage

```jinja
[% include "includes/units/hello-world.j2" %]
```

This renders the included snippet inline, allowing reuse and cleaner templates.

---

## 📌 Best Practices

* Store macros/helpers in `.tpl` files and import globally.
* Place reusable snippets under `includes/` for organization.
* Use clear, descriptive filenames and consistent naming.
* Avoid hardcoding variables; prefer injecting values with `[[ var_name ]]`.
* Use fallbacks and conditionals in templates to handle missing or optional variables.

---

## 📦 Full Example Walkthrough

### Step 1: Initialize Template Directory

```bash
git-pilot init --template-dir test1
```

### Step 2: Template and Supporting Files

#### `example.yml.j2` — Main Template

```jinja
name: [[ ci_name ]]

on:
  push:
    branches:
      - "[[ env ]]"

jobs:
  [[ job_id ]]:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      [[ include('units/hello-world.j2') | indent(6) ]]
```

* Uses injected variables like `ci_name`, `env`, and `job_id`.
* Includes reusable steps via the include directive.

#### `includes/_helpers.tpl` — Macro Helper

```jinja
[%- macro upper(s) -%]
[[ s.upper().strip() if s ]]
[%- endmacro -%]
```

Defines a global macro `upper()` for uppercase string transformation.

#### `includes/units/hello-world.j2` — Included Snippet

```yaml
- name: Hello World
  run: echo "Hello, World from job [[ _.upper(job_id) ]]!"
```

Prints a message using the uppercase macro on `job_id`.

#### `override-example.yml.j2` — Alternate Template

```jinja
name: [[ ci_name ]]

on:
  push:
    branches:
      - "[[ env ]]"

jobs:
  [[ job_id ]]:
    runs-on: ubuntu-latest
    steps:
      - name: Hello from [[ env ]]!
        run: echo "Hello, [[ job_id ]]!"
        env:
          SUPER_SECRET: ${{ secrets.SuperSecret }}
```

An alternate workflow template that can be selectively applied via regex matching.

#### `values.yml` — Configuration File

```yaml
defaults:
  branch: dev
  message: "git-pilot: update CI workflow"
  path: ".github/workflows"
  vars:
    ci_name: scan
  templates:
    - ".*\\.j2$"

repos:
  - name: r3d-shadow/git-pilot-test-1
    vars:
      job_id: container_scan1
      env: test

  - name: r3d-shadow/git-pilot-test-2
    branch: main
    message: "git-pilot: update CI workflow : Override"
    path: ".github/workflows/git-pilot/"
    vars:
      job_id: sast_scan123456
      env: stage
    templates:
      - "^override.*\\.j2$"
```

Defines defaults and per-repo overrides including branch, commit message, output path, variables, and template selection via regex.

---

### Step 3: Render and Sync Templates

Run:

```bash
cd test1

git-pilot sync \
  --token <GITHUB_TOKEN> \
  --template-dir ./ \
  --values ./values.yml
```

* Renders templates with injected variables.
* Shows a preview diff and summary of created/updated/deleted files.
* Commits and pushes changes to each target repository.

---