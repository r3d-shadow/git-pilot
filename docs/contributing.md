# 🤝 Contributing to `git-pilot`

First off, thank you for taking the time to contribute to `git-pilot`! 🎉
We welcome pull requests, issues, suggestions, and feedback from the community.

---

## 🧰 How to Contribute

There are many ways to help:

* 🐞 **Report bugs**
* 📚 **Improve documentation**
* 💡 **Suggest features or improvements**
* 🔧 **Submit code via pull requests**
* 🧪 **Write or improve tests**

---

## 🛠️ Development Setup

### 1. Clone the repo

```bash
git clone https://github.com/r3d-shadow/git-pilot.git
cd git-pilot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e "."
```

---

## 🚀 Submitting a Pull Request

1. Fork the repo and create a new branch:

   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes and write tests if applicable.

3. Commit your changes:

   ```bash
   git commit -m "feat: brief description of your change"
   ```

5. Push to your fork and create a pull request against the `dev` branch.

---

## 📁 Project Structure

```
src/
├── cli/               # CLI logic and args
├── commands/          # Command implementations like sync
├── config/            # values.yml loader and validation
├── core/              # Core engine, sync logic, interfaces
├── diff/              # Rich-powered diff viewer
├── providers/         # GitHub and other providers
├── state/             # Tracks local file hashes
├── template_engine/   # Jinja2 templating and helpers
├── utils/             # Logging, hashing, misc
tests/                 # Unit and integration tests
```

---

## 🧩 Good First Issues

Look for issues labeled:

* `good first issue`
* `help wanted`

---

## 🌟 Community Standards

* Be kind and respectful to others.
* Assume good intent.
* Use inclusive language.

---

## 🙌 Thanks

Every contribution — big or small — helps `git-pilot` grow.
We’re excited to build with you. 💙