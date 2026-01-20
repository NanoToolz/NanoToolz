# Basic git
git status
git add .
git commit -m "message"
git push origin main

# Repository already working
# Code already pushed to GitHub
# Basic git
git status
git add .
git commit -m "message"
git push origin main

# Repository already working
# Code already pushed to GitHub
🚀 Nanotoolz.me – Scalable Premium Telegram Store Bot built with Python (aiogram v3). Sell digital products, license keys, tools, courses & subscriptions.

## Git guide (short & practical)
Yeh README aapko git use karna sikhata hai — commands aur short description ke saath. Linux terminal assume kiya gaya hai.

### 1) Ek dafa global config (aapki identity)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 2) Project folder mein jao
```bash
cd /home/dev/Telegram\ Bots/NanoToolz
```

### 3) Naya repo shuru karna
```bash
git init
# Stage + commit
git add .
git commit -m "Initial commit"
# default branch ko main bananey ke liye:
git branch -M main
```

### 4) Remote (GitHub) add karna aur push karna
SSH:
```bash
git remote add origin git@github.com:username/repo.git
git push -u origin main
```
HTTPS:
```bash
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### 5) Remote se clone karna
```bash
git clone git@github.com:username/repo.git
# ya
git clone https://github.com/username/repo.git
```

### 6) Rozmarra ke commands (small workflow)
- Status dekhna:
```bash
git status
```
- Files stage + commit:
```bash
git add file.py
git commit -m "Short message"
# ya quick (saved changes only):
git commit -am "Update files"
```
- Branch create karna aur switch karna:
```bash
git checkout -b feature-branch
# branch switch:
git checkout main
```
- Changes fetch/pull:
```bash
git fetch
git pull
```
- Push:
```bash
git push origin feature-branch
```
- Merge local branch:
```bash
git checkout main
git merge feature-branch
```
- History:
```bash
git log --oneline --graph --decorate
```

### 7) .gitignore
Project mein unnecessary files ignore karne ke liye .gitignore banayein:
```text
__pycache__/
*.pyc
.env
config.json
```

### 8) Common tips
- Har commit chhota aur meaningful rakhein.
- Branch per feature develop karein, phir PR/merge karein.
- SSH keys set karne se pushes aasaan hotay hain (no password prompts).
- Sensitive data kabhi repo mein na rakhein — use environment variables / secrets.

### 9) Quick GitHub repo setup (web)
1. GitHub par new repo banayein.
2. Remote URL copy karein.
3. Terminal se remote add aur push karein (upar diye gaye commands).

---

References: git official docs — https://git-scm.com/docs
