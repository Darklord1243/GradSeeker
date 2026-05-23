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

1. **Zip your project locally** (exclude `instance/database.db`, `__pycache__`, `venv/`)
2. **In PythonAnywhere:**
   - Go to **Files** tab
   - Navigate to `/home/yourusername/`
   - Click **Upload a file**
   - Upload the zip file
   - Click on the zip file → **Extract**

**Files to Upload:**

```
GradSeeker/
├── app.py
├── models.py
├── load_data.py
├── utils.py
├── requirements.txt
├── universities.csv
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── map.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── browse.html
│   ├── universities.html
│   ├── programs.html
│   ├── program_detail.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── instance/  (empty folder - database will be created)
```

**Files to EXCLUDE:**

- `instance/database.db` (will be created on server)
- `__pycache__/` folders
- `venv/` or `xjco2011_env/` (virtual environments)
- `.git/` folder (if using Git)
- `tests/` folder (optional - not needed for deployment)

---

### Step 11.3: Install Dependencies

1. **Open Bash Console:** **Consoles** tab → **Bash**
2. **Navigate to project:** `cd ~/GradSeeker`
3. **Install dependencies:**

```bash
pip3.10 install --user -r requirements.txt
```

Use `pip3.10` and `--user` on the PythonAnywhere free tier.

4. **Verify installation:**

```bash
python3.10 -c "import flask; print(flask.__version__)"
```

---

### Step 11.4: Initialize Database

1. **In Bash console:**

```bash
cd ~/GradSeeker
python3.10
```

2. **In Python shell:**

```python
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created successfully!")
exit()
```

3. **Verify database created:**

```bash
ls -la instance/
```

---

### Step 11.5: Load Data

1. **In Bash console:**

```bash
cd ~/GradSeeker
python3.10 load_data.py
```

2. **Verify data loaded (optional):**

```python
from app import create_app
from models import db, University, Program

app = create_app()
with app.app_context():
    print(f"Universities: {University.query.count()}")
    print(f"Programs: {Program.query.count()}")
```

---

### Step 11.6: Configure WSGI File

1. Go to the **Web** tab → **Add a new web app** (or edit existing)
2. Choose **Flask** and **Python 3.10**
3. Edit the WSGI configuration file and replace its contents with:

```python
import sys

project_home = '/home/yourusername/GradSeeker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app
application = create_app()
```

Replace `yourusername` with your PythonAnywhere username.

---

### Step 11.7: Configure Static Files

In **Web** tab → **Static files**:

- **URL:** `/static/`
- **Directory:** `/home/yourusername/GradSeeker/static/`

---

### Step 11.8: Update SECRET_KEY for Production

1. Generate a secure key:

```bash
python3.10 -c "import secrets; print(secrets.token_hex(32))"
```

2. **Recommended:** set `SECRET_KEY` in **Web** tab → **Environment variables**

3. **Alternative:** update `app.py` on the server (less secure than env vars):

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

Never commit production secret keys to Git.

---

### Step 11.9: Reload Web App

Go to **Web** tab → click **Reload** → check the error log if anything fails.

---

### Step 11.10: Test Deployed Site

Visit `http://yourusername.pythonanywhere.com/` and verify:

- [ ] Home page loads
- [ ] Browse page shows map
- [ ] Country → university → program navigation works
- [ ] Register, login, dashboard, and shortlist work
- [ ] Compatibility calculator works
- [ ] CSS and JavaScript load correctly
- [ ] Layout is usable on mobile

Check **Web** tab → **Error log** if anything fails.

---

## Troubleshooting Common Issues

### Issue 1: `ModuleNotFoundError: No module named 'flask'`

```bash
pip3.10 install --user -r requirements.txt
```

### Issue 2: Database not found or tables missing

```python
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
```

### Issue 3: Static files not loading

1. Check **Web** tab → **Static files** mapping
2. Verify path: `/home/yourusername/GradSeeker/static/`
3. Check permissions: `chmod 755 static/` and `chmod 644 static/css/*`

### Issue 4: Internal Server Error

Check the **Error log** in the **Web** tab for import, database, or syntax errors.

### Issue 5: WSGI / application not found

Verify the WSGI file path and that `application = create_app()` is set correctly.

### Issue 6: Database locked errors

Ensure only one process accesses SQLite at a time. Restart the web app if needed.

---

## Security Notes

1. Change `SECRET_KEY` from the development default before production
2. SQLite files should not be publicly accessible (PythonAnywhere handles this)
3. Passwords are hashed with Werkzeug
4. Validate all user inputs server-side (already implemented in the app)

---

## Success Criteria (RFC 11)

- [ ] App deployed to PythonAnywhere
- [ ] Database initialized on server
- [ ] Data loaded successfully
- [ ] Site accessible via URL
- [ ] All features work on deployed site

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
