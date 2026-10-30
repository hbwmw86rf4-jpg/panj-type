# Publish this folder as a public GitHub repo

From a machine where you are logged into GitHub (`gh auth login`):

```bash
cd panj-type
git init
git add .
git commit -m "Initial release: Panj Type Gurmukhi families under the SIL OFL 1.1"
gh repo create panj-type --public --source=. --remote=origin --push --description "Free open-source Gurmukhi (Punjabi) fonts — seven families in the roles of popular Latin type"
```

Suggested topics on the GitHub repo page: `gurmukhi`, `punjabi`, `fonts`, `ofl`, `typeface`.

Or create an empty public repository named `panj-type` on github.com, then:

```bash
git remote add origin https://github.com/hbwmw86rf4-jpg/panj-type.git
git branch -M main
git push -u origin main
```
