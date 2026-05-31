# Installation and GitHub Setup

This guide covers local installation, development installation, test execution, and pushing the package to GitHub.

## 1. Recommended local setup

From the package root:

```bash
cd universal-output-hub
python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install the package in editable development mode:

```bash
python -m pip install -e ".[dev,examples]"
```

## 2. Smoke test

```bash
python examples/example_basic.py
```

Expected result: an output folder is created with regression tables, ordinary tables, `manifest.json`, and `index.html`.

## 3. Run tests

```bash
pytest -q
```

## 4. Use inside another Python project

From a local path:

```bash
python -m pip install -e "C:\path\to\universal-output-hub"
```

Then use:

```python
from universal_output_hub import OutputHub
```

## 5. Push to GitHub using Git CLI

Create an empty GitHub repository first, for example:

```text
Akanom/universal-output-hub
```

Then run from the package root:

```bash
git init
git add .
git commit -m "Initial release: universal output hub"
git branch -M main
git remote add origin https://github.com/Akanom/universal-output-hub.git
git push -u origin main
```

If Git asks who you are:

```bash
git config --global user.name "Oluwajuwon Akanbi"
git config --global user.email "YOUR_GITHUB_EMAIL@example.com"
```

## 6. Push to GitHub using GitHub CLI

If GitHub CLI is installed and authenticated:

```bash
gh repo create Akanom/universal-output-hub --public --source=. --remote=origin --push
```

For a private repository:

```bash
gh repo create Akanom/universal-output-hub --private --source=. --remote=origin --push
```

## 7. Install directly from GitHub after pushing

```bash
python -m pip install git+https://github.com/Akanom/universal-output-hub.git
```

Editable install from a cloned repository:

```bash
git clone https://github.com/Akanom/universal-output-hub.git
cd universal-output-hub
python -m pip install -e ".[dev,examples]"
```

## 8. One-command push scripts

After creating an empty repository on GitHub, you can use the included scripts.

Windows PowerShell:

```powershell
.\scripts\push_to_github.ps1 Akanom/universal-output-hub
```

macOS/Linux/Git Bash:

```bash
./scripts/push_to_github.sh Akanom/universal-output-hub
```
