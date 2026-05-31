param(
    [string]$RepoFullName = "Akanom/universal-output-hub"
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/$RepoFullName.git"

if (-not (Test-Path ".git")) {
    git init
}

git add .
$staged = git diff --cached --name-only
if ($staged) {
    git commit -m "Initial release: universal output hub"
} else {
    Write-Host "No changes to commit."
}

git branch -M main
$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

git push -u origin main
