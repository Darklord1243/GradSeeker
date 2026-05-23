# GradSeeker Deployment Guide
## RFC 11: PythonAnywhere Deployment

**Version:** 1.0  
**Date:** December 2024  
**Target:** PythonAnywhere (Free Tier)  
**SRS Reference:** NFR-13, NFR-14

---

## Pre-Deployment Checklist

Before starting, ensure you have:

- [ ] PythonAnywhere account created (free tier is sufficient)
- [ ] All code tested locally and working
- [ ] `requirements.txt` file present and up-to-date
- [ ] `universities.csv` file ready
- [ ] Database can be created and populated locally
- [ ] All static files (CSS, JS) are in `static/` folder

---

## Step-by-Step Deployment

### Step 11.1: PythonAnywhere Account Setup

1. **Create Account:**
   - Go to https://www.pythonanywhere.com/
   - Click "Sign up for free"
   - Create account (free tier is sufficient)

2. **Verify Python Version:**
   - PythonAnywhere uses Python 3.10 by default (compatible with our app)
   - You can verify in the **Consoles** tab → **Bash console**

3. **Access Dashboard:**
   - After logging in, you'll see the dashboard
   - Key tabs: **Files**, **Web**, **Consoles**, **Tasks**

---

### Step 11.2: Upload Code to PythonAnywhere

**Option A: Using Git (Recommended)**

```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/Darklord1243/GradSeeker.git
cd GradSeeker
```

**Option B: Manual Upload via Files Tab**

1. Zip your project locally (exclude `instance/database.db`, `__pycache__`, `venv/`)
2. Upload and extract via the **Files** tab

**Files to EXCLUDE:**

- `instance/database.db` (will be created on server)
- `__pycache__/` folders
- `venv/` or `xjco2011_env/` (virtual environments)
- `.git/` folder (if using Git)
- `tests/` folder (optional - not needed for deployment)

---

### Step 11.3: Install Dependencies

```bash
cd ~/GradSeeker
pip3.10 install --user -r requirements.txt
python3.10 -c "import flask; print(flask.__version__)"
```

---

### Step 11.4: Initialize Database

```bash
cd ~/GradSeeker
python3.10
```

```python
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created successfully!")
exit()
```

---

### Step 11.5: Load Data

```bash
cd ~/GradSeeker
python3.10 load_data.py
```

---

### Step 11.6: Configure WSGI File

In the PythonAnywhere **Web** tab, edit the WSGI file:

```python
import sys

project_home = '/home/yourusername/GradSeeker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app
application = create_app()
```

Replace `yourusername` with your actual PythonAnywhere username.

---

### Step 11.7: Configure Static Files

In **Web** tab → **Static files**:

- **URL:** `/static/`
- **Directory:** `/home/yourusername/GradSeeker/static/`

---

### Step 11.8: Update SECRET_KEY for Production

Generate a secure key:

```bash
python3.10 -c "import secrets; print(secrets.token_hex(32))"
```

Set it via environment variable in the **Web** tab, or update `app.py` on the server. Prefer environment variables over hard-coding.

---

### Step 11.9: Reload Web App

Go to **Web** tab → click **Reload** → check the error log if anything fails.

---

### Step 11.10: Test Deployed Site

Visit `http://yourusername.pythonanywhere.com/` and verify:

- Home, browse, universities, programs, and program detail pages
- Register, login, dashboard, shortlist, compatibility calculator
- CSS, JavaScript map, and mobile layout

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | `pip3.10 install --user -r requirements.txt` |
| Database / table errors | Run `db.create_all()` inside app context |
| Static files broken | Check static file mapping in **Web** tab |
| Internal Server Error | Read **Error log** in **Web** tab |

---

## Post-Deployment Checklist

- [ ] Site is accessible at your PythonAnywhere URL
- [ ] Database is populated with data
- [ ] User registration/login works
- [ ] All features functional
- [ ] Site remains live (NFR-14: 3 weeks minimum)

---

## Additional Resources

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask on PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/)
- [Static Files](https://help.pythonanywhere.com/pages/StaticFiles/)

**Document Status:** Ready for Deployment  
**Last Updated:** December 2024
