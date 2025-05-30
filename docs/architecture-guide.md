# 🧱 git-pilot Technical Architecture Guide

This guide provides a technical overview of how `git-pilot` works under the hood. It is intended for engineers looking to understand the internals of the system, its architecture, extension points, and the overall sync lifecycle.

---

## 📦 Project Structure

```
src/
├── cli/               # Command-line interface and argument parsing
├── commands/          # CLI command implementations (sync, init, etc.)
├── config/            # YAML configuration loader and schema handling
├── core/              # Core logic: sync engine, comparator, facade
├── diff/              # Diff generation and interactive diff viewer
├── providers/         # Git hosting providers (e.g., GitHub)
├── state/             # Local file state tracking (hashes, history)
├── template_engine/   # Jinja2 templating system and helper registration
├── utils/             # Common utilities (hashing, logging)
```

---

## 🧠 Core Concepts

### 1. **Clean Architecture and Interfaces**

* Every subsystem (template engine, state manager, provider) exposes a well-defined interface.
* The `SyncEngine` only interacts with these interfaces, not their implementations.
* This ensures modularity, testability, and pluggability.

### 2. **Template Rendering Engine**

* Based on **Jinja2**, enhanced with custom delimiters `[[ ]]` and `[% %]` to avoid GitHub Actions conflicts.
* Supports includes (`include()`), macros (`.tpl` files), and custom helper functions (`to_yaml`, `tpl`, `indent`).
* Templating logic lives in `template_engine/jinja_loader.py`.

### 3. **Configuration System**

* The `values.yml` file defines global defaults and per-repository overrides:

  * Branch, commit message, file path
  * Regex patterns for template selection
  * Variables for injection into templates
* Configuration is parsed by `config/loader.py`

### 4. **Sync Lifecycle**

```text
1. Load config (values.yml)
2. Select templates based on regex patterns
3. For each repo:
    a. Render templates with variables
    b. Compare rendered output with previous local state
    c. Show interactive diff view
    d. Sync changes using the provider
    e. Update local state file
```

### 5. **Diff Viewer**

* Powered by **Rich** for terminal rendering.
* Shows created, updated, and deleted files with inline diffs.
* Users can scroll and toggle files interactively before syncing.

### 6. **Provider Abstraction**

* Current implementation: `GitHubProvider` using **PyGitHub**.
* Exposes standard methods:

  * `push_file()`
  * `delete_file()`
  * `get_file()`
* Additional providers (GitLab, Bitbucket) can be added by implementing the same interface.

### 7. **State Management**

* Uses a local JSON file to track previously synced templates and their rendered SHA.
* Allows detection of renamed, updated, or removed workflows across runs.
* Ensures safe cleanup and avoids redundant syncs.

---

## 🧩 Templating Internals

* All templates must end with `.j2`
* `includes/units/*.j2`: reusable blocks injected into templates
* `_helpers.tpl`: global macro definitions (e.g., `upper()`, `default()`, etc.)
* Templates can call macros like: `[[ _.upper(job_id) ]]`
* Includes are rendered with indentation control via `| indent(N)`

---

## 🔧 Extension Points

| Component        | Extension Strategy                                            |
| ---------------- | ------------------------------------------------------------- |
| Providers        | Add new file under `providers/`, register class with factory  |
| Template Helpers | Define macros in `_helpers.tpl`                               |
| Template Layout  | Follow Helm-style `includes/`, `templates/` structure         |
| CLI Commands     | Add new command in `commands/`, register in `cli/commands.py` |

---