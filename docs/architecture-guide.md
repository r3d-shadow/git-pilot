# 🧱 git-pilot Technical Architecture Guide

This guide provides a technical overview of how **git-pilot** works under the hood. It is intended for engineers and contributors seeking to understand the system architecture, key components, extension points, and the overall synchronization lifecycle.

---

## 📦 Project Structure

```
src/
├── cli/               # Command-line interface and argument parsing
├── commands/          # CLI command implementations (e.g., sync, init)
├── config/            # YAML config loader and schema validation
├── core/              # Core business logic: sync engine, facade, diff comparison
├── diff/              # Diff generation, interactive diff viewer UI
├── providers/         # Git hosting provider integrations (GitHub, etc.)
├── state/             # Local sync state storage and management
├── template_engine/   # Jinja2 templating setup, custom delimiters, helpers
├── utils/             # Shared utilities (logging, hashing, helpers)
```

---

## 🧠 Core Concepts

### 1. **Clean Architecture & Interface-driven Design**

* Each subsystem (template engine, state manager, provider) exposes clear, minimal interfaces.
* The central `SyncEngine` depends only on these interfaces, promoting modularity and ease of testing.
* Enables pluggable providers and templating engines without impacting core logic.

### 2. **Template Rendering Engine**

* Built on **Jinja2**, extended with custom delimiters:

  * Variables: `[[ ... ]]`
  * Statements: `[% ... %]`
* Supports:

  * Includes (`include()`) for reusable partials.
  * Macros stored in `.tpl` helper files (e.g., `_helpers.tpl`).
  * Custom helper functions like `upper()`, `indent()` etc
* Implementation lives in `template_engine/jinja_loader.py`.

### 3. **Configuration System**

* `values.yml` defines:

  * Global defaults (branch, commit message, output path).
  * Repository-specific overrides, including:
    * Regex filters for selecting templates.
    * Per-repo injected variables.
* Configuration parsing and validation handled by `config/loader.py`.

### 4. **Sync Lifecycle**

```text
1. Load and validate configuration (values.yml)
2. Select applicable templates per repository using regex filters
3. For each repository:
    a. Render templates with injected variables
    b. Compare rendered output to local cached state (hash comparison)
    c. Show interactive terminal diff preview using Rich
    d. Sync changes (create/update/delete) via the provider API
    e. Persist updated state locally for next run
```

### 5. **Diff Viewer**

* Interactive terminal UI powered by **Rich**.
* Presents a clear summary of:
  * Created files
  * Updated files with inline diffs
  * Deleted files
* Allows user scrolling, expanding/collapsing diffs before confirming sync.

### 6. **Provider Abstraction**

* Current provider: **GitHubProvider** using [PyGitHub](https://pygithub.readthedocs.io/).
* Standardized interface methods:

  * `push_file(path, content, branch, message)`
  * `delete_file(path, branch, message)`
  * `get_file(path, branch)`
* Supports adding new providers (GitLab, Bitbucket, etc.) by implementing the same interface.

### 7. **State Management**

* Local JSON file tracks:
  * Previously synced files per repo
  * SHA hashes of rendered templates
* Enables detection of:
  * Updated workflows
  * Deleted/renamed files
* Ensures safe cleanup and idempotent sync operations.

---

## 🧩 Templating Internals

* Templates end with `.j2`.
* Reusable snippets placed under `includes/units/`.
* Global macros in `_helpers.tpl`, e.g., `upper()`, `default()`.
* Templates invoke macros as `[[ _.upper(var_name) ]]`.
* Includes support indentation control via Jinja2 filters (`| indent(n)`).

---

## 🔧 Extension Points

| Component            | How to Extend                                                           |
| -------------------- | ----------------------------------------------------------------------- |
| **Providers**        | Add a new provider module in `providers/`; register in factory          |
| **Template Helpers** | Define macros in `_helpers.tpl` or create new `.tpl` files              |
| **Template Layout**  | Follow Helm-style directory structure with `includes/` and `templates/` |
| **CLI Commands**     | Add new commands in `commands/` and register in `cli/commands.py`       |

---