# 🚀 git-pilot Roadmap

This roadmap outlines planned features, improvements, and milestones for **git-pilot** to guide development priorities and community contributions.

---

## 🎯 Vision

Enable seamless, automated synchronization of templated CI/CD workflows, configuration files across multiple Git repositories, with a clean, extensible architecture supporting multiple providers and flexible templating.

---

## 📅 Near-Term (Next 0–1 months)

### Core Enhancements

* [x] Complete interactive diff viewer with Rich integration
* [x] Support regex-based template selection per repo
* [x] Implement local state tracking for idempotent syncs
* [x] Add comprehensive tests for sync engine and template rendering
* [x] Improve CLI UX and error messages
* [x] Create a GitHub Action Marketplace integration for easy adoption

### Provider Support

* [x] Fully support GitHub via PyGitHub
* [ ] Add support for GitLab repositories (community help welcome)
* [ ] PR based commits

### Templating

* [x] Finalize Helm-style Jinja2 templating with macros and includes
* [ ] Implement additional helper macros (e.g., string utilities)

### Documentation & Tooling

* [x] Publish templating guide and technical architecture docs
* [x] Set up CI/CD pipelines for automated releases
* [ ] Add contributor guide and developer onboarding docs
* [ ] Set up CI/CD pipelines for automated testing

---

## 🔮 Mid-Term (1–2 months)

### Feature Expansion

* [ ] Add support for secrets and environment variable injection with secure handling
* [ ] Enhanced interactive previews
* [ ] Implement caching and parallel sync for improved performance across large repo sets

### Multi-provider Support

* [ ] Implement Bitbucket provider integration
* [ ] Abstract provider interfaces for seamless addition of new SCM platforms

### UX Improvements

* [ ] Enhance diff viewer with side-by-side diffs and search/filter capabilities
---

## 🌟 Long-Term (2+ months)

### Ecosystem Growth

* [ ] Develop a web UI/dashboard for monitoring sync status and managing repos
* [ ] Build plugin architecture to allow community-contributed templates and providers

### Advanced Features

* [ ] Integrate policy-as-code checks before sync (e.g., validate workflows against org policies)
* [ ] Support for incremental and partial template updates
* [ ] Add multi-branch and multi-environment sync capabilities

---

## 🧩 How to Contribute

* Check the [contribution guidelines](contributing.md)
* Join discussions in GitHub Issues
* Pick issues tagged `help wanted` or `good first issue`
* Submit pull requests with tests and documentation updates