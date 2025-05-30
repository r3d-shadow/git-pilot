# 🧠 Templating Guide

`git-pilot` uses a Helm-style templating engine built on Jinja2 to render GitHub Actions workflows. This guide walks through the templating features and best practices.

---

## 🧱 Template Files

Templates are Jinja2 files ending in `.j2`. You can organize templates into logical directories and use shared partials or macros.

* **Templates**: Full files rendered to target repos (e.g. `example.yml.j2`)
* **Includes**: Reusable chunks included in templates (e.g. `includes/units/*.j2`)
* **Helpers**: `.tpl` macro files with reusable logic (e.g. `_helpers.tpl`)

---

## 🔀 Custom Delimiters

To avoid syntax collisions with GitHub Actions YAML files, `git-pilot` uses custom delimiters:

| Purpose         | Syntax                             |
| --------------- | ---------------------------------- |
| Variable        | `[[ variable ]]`                   |
| Statement/Block | `[% if condition %]...[% endif %]` |

---

## ⚙️ Template Functions

You can use any Jinja2 feature along with these custom helpers available globally:

| Function        | Description                                |
| --------------- | ------------------------------------------ |
| `tpl(str)`      | Evaluates a string as a Jinja2 template    |
| `to_yaml(obj)`  | Converts an object to indented YAML        |
| `indent(n, s)`  | Indents string `s` with `n` spaces         |
| `capitalize(s)` | Capitalizes the first letter of string `s` |

---

## 📥 Includes and Macros

You can break templates into reusable includes and macros for composability.

### Example Include:

```jinja
# templates/includes/units/hello-world.j2
name: hello-world
run: echo "Hello [[ name ]]!"
```

### Usage in Template:

```jinja
[% include "includes/units/hello-world.j2" %]
```

---

## 📌 Best Practices

* Use `.tpl` for helper macros and import them globally
* Group includes under `includes/` for clarity
* Use descriptive file names and consistent patterns
* Avoid hardcoding variables—prefer `[[ some_var ]]` with fallbacks

---

## 📦 Example

This example shows how templates, includes, macros, and `values.yml` work together.

### 1. Initialize a Template Directory

```bash
git-pilot init --template-dir test1
```

### 2. Template and Config Files

#### 📄 `./example.yml.j2`

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

This is your main template, where dynamic variables like `ci_name`, `env`, and `job_id` are rendered. It also includes a reusable job step using `include()`.

#### 📄 `./includes/_helpers.tpl`

```jinja
[%- macro upper(s) -%]
[[ s.upper().strip() if s ]]
[%- endmacro -%]
```

This macro is globally accessible and can be used for transformations like making strings uppercase.

#### 📄 `./includes/units/hello-world.j2`

```yaml
- name: Hello World
  run: echo "Hello, World from job [[ _.upper(job_id) ]]!"
```

This reusable unit prints a message with the job ID in uppercase, using the helper macro.

#### 📄 `./override-example.yml.j2`

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

This is an alternate template to be applied only to selected repos using regex-based matching.

#### 📄 `./values.yml`

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

Defines default behaviors and overrides per repository. The `templates` field supports regex to control which templates apply to which repos.

---

### 3. Run Git Sync

```bash
cd test1

git-pilot sync \
  --token <GITHU_TOKEN> \
  --template-dir ./ \
  --values ./values.yml
```

This will render templates using the provided values, preview a comparison view of all changes, and summarize created, updated, and deleted files before committing anything.