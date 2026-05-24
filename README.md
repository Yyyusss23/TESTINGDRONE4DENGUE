# 🚁 Drone4Dengue — Test Script Setup & Run Guide

> **System Testing Level** | Selenium (Web) + Appium (Mobile)  
> Testers: Edwin Tan Yu Xian · Brendan · Izzatul Filzah bt Norazmi · Auni Nafisa bt Osman · Yusrina Maisarah bt Yunus

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Structure](#2-project-structure)
3. [One-Time Setup](#3-one-time-setup)
   - [3.1 Clone Project](#31-clone--open-project)
   - [3.2 Python Virtual Environment](#32-python-virtual-environment)
   - [3.3 Backend API (.env)](#33-backend-api-env)
   - [3.4 Mobile App (.env)](#34-mobile-app-env)
   - [3.5 Database Setup](#35-database-setup)
   - [3.6 Android SDK Path](#36-android-sdk-path)
   - [3.7 Appium Driver](#37-appium-driver)
4. [Test Users in Database](#4-test-users-in-database)
5. [Running Selenium Web Tests](#5-running-selenium-web-tests)
   - [5.1 Start Servers](#51-start-servers)
   - [5.2 Verify Setup](#52-verify-setup)
   - [5.3 Run Scripts](#53-run-web-test-scripts)
6. [Running Appium Mobile Tests](#6-running-appium-mobile-tests)
   - [6.1 Start API Server](#61-start-api-server)
   - [6.2 Start Emulator](#62-start-android-emulator)
   - [6.3 Start Expo App](#63-start-expo-app)
   - [6.4 Start Appium](#64-start-appium-server)
   - [6.5 Run Scripts](#65-run-mobile-test-scripts)
7. [Mailtrap Email Setup (UC3)](#7-mailtrap-email-setup-uc3-only)
8. [All Test Scripts Reference](#8-all-test-scripts-reference)
9. [Common Errors & Fixes](#9-common-errors--fixes)
10. [Quick Commands Cheatsheet](#10-quick-commands-cheatsheet)

---

## 1. Prerequisites

Install all tools below before running any test script.

| Tool | Version | How to Verify |
|------|---------|---------------|
| Node.js | v18+ | `node --version` |
| npm | v9+ | `npm --version` |
| Python | v3.10+ | `python3 --version` |
| Google Chrome | Latest | Open Chrome → Settings → About |
| ChromeDriver | Match Chrome version | Auto-managed by Selenium 4 |
| Android Studio | Latest stable | Open Android Studio |
| Android SDK | API Level 33+ | Android Studio → SDK Manager |
| ADB | Bundled with SDK | `adb --version` |
| Appium | v2.x | `appium --version` |
| Appium UiAutomator2 | Latest | `appium driver list --installed` |
| Expo CLI | Auto via npx | `npx expo --version` |

> **macOS:** Use Homebrew → `brew install node python`  
> **Windows:** Use official installers from nodejs.org and python.org

---

## 2. Project Structure

```
drone4dengue/
├── server-api/              ← Backend API (Express + Prisma + SQLite)
│   ├── .env                 ← API environment variables (create this)
│   ├── prisma/
│   │   └── dev.db           ← SQLite database
│   └── index.js
├── client-admin/            ← Admin Web (Next.js)
│   ├── .env.local           ← Web environment variables
│   ├── UC1_Login_Web_Test.py
│   ├── UC3_web_reset_password.py
│   ├── UC4_edit_profile.py
│   └── UC1_screenshots/     ← Web test screenshots (auto-created)
├── client-mobile/           ← Mobile App (React Native + Expo)
│   ├── .env                 ← Mobile environment variables (create this)
│   ├── UC1_Login_Mobile_Test.py
│   ├── UC3_mobile_reset_password.py
│   ├── UC4_mobile_edit_profile.py
│   └── UC1_mobile_screenshots/ ← Mobile test screenshots (auto-created)
└── .venv/                   ← Python virtual environment (create this)
```

---

## 3. One-Time Setup

> Do these steps **once** before running any tests.

### 3.1 Clone / Open Project

```bash
cd /path/to/drone4dengue
# Or on Windows:
cd C:\Users\YourName\Documents\drone4dengue
```

---

### 3.2 Python Virtual Environment

Create and activate the virtual environment, then install all Python dependencies.

**macOS / Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate
# Prompt changes to: (.venv)

# Install dependencies
pip install selenium
pip install Appium-Python-Client
pip install webdriver-manager
```

**Windows:**
```cmd
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate
# Prompt changes to: (.venv)

# Install dependencies
pip install selenium
pip install Appium-Python-Client
pip install webdriver-manager
```

> **Verify:** `python -c "import selenium; print(selenium.__version__)"`

---

### 3.3 Backend API (.env)

Create the file `server-api/.env` with the following content:

```env
# Database
DATABASE_URL="file:./dev.db"

# Auth
JWT_SECRET="your-secret-key-here"
PORT=4000

# Mailtrap SMTP (for UC3 Reset Password tests)
# Get credentials from https://mailtrap.io → Email Testing → My Inbox → SMTP Settings
SENDER_EMAIL="your-mailtrap-username"
SENDER_EMAIL_PW="your-mailtrap-password"
```

**Generate a JWT secret:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

### 3.4 Mobile App (.env)

Create the file `client-mobile/.env` with the following content:

```env
# Android emulator routes 10.0.2.2 → your computer's localhost
# DO NOT use localhost:4000 — it will not work on the emulator
EXPO_PUBLIC_API_URL=http://10.0.2.2:4000

# Optional — Google Maps (only needed for map screens)
# EXPO_PUBLIC_GOOGLE_MAPS_API_KEY=your-key-here
```

> ⚠️ **Windows users:** If the path separator causes issues, use forward slashes in .env values.

---

### 3.5 Database Setup

Install dependencies and create the SQLite database:

```bash
cd server-api

# Install Node dependencies
npm install

# Run Prisma migrations (creates dev.db)
npx prisma migrate dev --name init

# Generate Prisma client
npx prisma generate
```

---

### 3.6 Android SDK Path (macOS/Linux)

Add Android SDK to your PATH so `adb` commands work anywhere:

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export ANDROID_HOME=$HOME/Library/Android/sdk' >> ~/.zshrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.zshrc
source ~/.zshrc

# Verify
adb --version
```

**Windows:** Add `C:\Users\YourName\AppData\Local\Android\Sdk\platform-tools` to System Environment Variables → PATH.

---

### 3.7 Appium Driver

```bash
# Install Appium globally
npm install -g appium

# Install Android UiAutomator2 driver
appium driver install uiautomator2

# Verify both are installed
appium driver list --installed
```

---

## 4. Test Users in Database

Create these users in the database **before running any tests**.

**Step 1 — Start the API server:**
```bash
cd server-api && npm run dev
```

**Step 2 — Open Prisma Studio:**
```bash
# New terminal
cd server-api
npx prisma studio
# Opens at http://localhost:5555
```

**Step 3 — Generate password hashes:**
```bash
# Hash for 'drone123' (admin web user)
node -e "const b=require('bcrypt');b.hash('drone123',10).then(console.log)"

# Hash for 'Mobile12!' (mobile user)
node -e "const b=require('bcrypt');b.hash('Mobile12!',10).then(console.log)"

# Hash for 'ValidPass123!' (non-admin user)
node -e "const b=require('bcrypt');b.hash('ValidPass123!',10).then(console.log)"
```

**Step 4 — Create users in Prisma Studio:**

| Email | Password | Role | Used In |
|-------|----------|------|---------|
| `good@email.com` | drone123 | `admin` | UC3 Web, UC4 Web |
| `admin@drone4dengue.com` | AdminSecurePass123! | `admin` | UC1 Web |
| `mobiletest@email.com` | Mobile12! | `user` | UC3 Mobile, UC4 Mobile, UC1 Mobile |
| `public_user@siswa.um.edu.my` | ValidPass123! | `user` | UC1 Web (non-admin test) |

> ⚠️ `ghost_user@siswa.um.edu.my` must **NOT** exist in the database (used as unregistered email test).

**Step 5 — Verify users exist:**
```bash
cd server-api
node -e "
const{PrismaClient}=require('@prisma/client');
const p=new PrismaClient();
p.user.findMany({select:{email:true,role:true,name:true}})
.then(u=>{console.log(JSON.stringify(u,null,2));p.\$disconnect();});
"
```

---

## 5. Running Selenium Web Tests

### 5.1 Start Servers

Open **two separate terminals** and start in this order:

**Terminal 1 — API Server:**
```bash
# Kill any existing process on port 4000 first
lsof -ti:4000 | xargs kill -9    # macOS/Linux
# Windows: netstat -ano | findstr :4000  then  taskkill /PID <pid> /F

cd server-api
npm run dev
# Wait for: Server running on port 4000
```

**Terminal 2 — Admin Web:**
```bash
cd client-admin
npm install          # Only needed first time
npm run dev
# Wait for: ready on http://localhost:3000
```

---

### 5.2 Verify Setup

Open your browser and check both URLs load:

```
http://localhost:3000   → should show login page
http://localhost:4000   → should show any JSON response
```

---

### 5.3 Run Web Test Scripts

Open **Terminal 3** and activate the virtual environment first:

**macOS/Linux:**
```bash
source /path/to/drone4dengue/.venv/bin/activate
```

**Windows:**
```cmd
.venv\Scripts\activate
```

Then run the test script you need:

**UC1 Login (Web):**
```bash
# macOS/Linux
python client-admin/UC1_Login_Web_Test.py

# Windows
python client-admin\UC1_Login_Web_Test.py
```

**UC3 Reset Password (Web):**
```bash
python client-admin/UC3_web_reset_password.py
```

**UC4 Edit Profile (Web):**
```bash
python client-admin/UC4_edit_profile.py
```

> Chrome opens automatically. Test results print to terminal. Press Enter when done to close the browser.  
> Screenshots are saved to `client-admin/UC1_screenshots/` etc.

---

## 6. Running Appium Mobile Tests

Mobile tests need **4 things running simultaneously** in separate terminals.

### 6.1 Start API Server

**Terminal 1:**
```bash
lsof -ti:4000 | xargs kill -9   # Kill if already running (macOS/Linux)
cd server-api
npm run dev
# Wait for: Server running on port 4000
```

---

### 6.2 Start Android Emulator

1. Open **Android Studio**
2. Go to **Device Manager** (right sidebar or Tools menu)
3. Click the **Play ▶** button next to your AVD (Android Virtual Device)
4. Wait for the emulator to fully boot (lock screen appears)

**Verify the emulator is connected:**
```bash
adb devices
# Must show:
# emulator-5554   device
```

> If it shows `offline` or nothing, wait 30 more seconds and try again.

---

### 6.3 Start Expo App

**Terminal 2:**
```bash
cd client-mobile
npm install          # Only needed first time
npx expo start

# When Metro bundler is ready, press 'a' to open on Android emulator
```

Wait until the app is fully loaded on the emulator screen (Login screen visible).

**If Google Maps error appears:** Tap **"Go To Home"** or **"Continue"** to bypass — Maps API key is restricted to the developer.

---

### 6.4 Start Appium Server

**Terminal 3:**
```bash
appium
# Wait for: Appium REST http interface listener started on 0.0.0.0:4723
```

> Leave this terminal running throughout testing. Do not close it.

---

### 6.5 Run Mobile Test Scripts

Open **Terminal 4** and activate virtual environment:

**macOS/Linux:**
```bash
source /path/to/drone4dengue/.venv/bin/activate
```

**Windows:**
```cmd
.venv\Scripts\activate
```

**Before running:** Make sure the emulator shows the **Login screen** of the DroneEye app.

**UC1 Login (Mobile):**
```bash
# macOS/Linux
python client-mobile/UC1_Login_Mobile_Test.py

# Windows
python client-mobile\UC1_Login_Mobile_Test.py
```

**UC3 Reset Password (Mobile):**
```bash
python client-mobile/UC3_mobile_reset_password.py
```

**UC4 Edit Profile (Mobile):**
```bash
python client-mobile/UC4_mobile_edit_profile.py
```

> Appium controls the emulator automatically. Do not touch the emulator while tests are running.  
> Screenshots are saved to `client-mobile/UC1_mobile_screenshots/` etc.

---

## 7. Mailtrap Email Setup (UC3 Only)

UC3 Reset Password tests require an email service. Since the Google API key is restricted to the developer, we use **Mailtrap** as a testing substitute.

### Step 1 — Create Mailtrap account
Go to [https://mailtrap.io](https://mailtrap.io) and sign up for a free account.

### Step 2 — Get SMTP credentials
After login: **Email Testing → My Inbox → Show Credentials / SMTP Settings**

Copy these values:
```
Host:     sandbox.smtp.mailtrap.io
Port:     2525
Username: your-mailtrap-username
Password: your-mailtrap-password
```

### Step 3 — Update server-api/.env
```env
SENDER_EMAIL="your-mailtrap-username"
SENDER_EMAIL_PW="your-mailtrap-password"
```

### Step 4 — Restart the API server
```bash
# Kill and restart
lsof -ti:4000 | xargs kill -9
cd server-api && npm run dev
```

### Step 5 — Verify email works
```bash
curl -X POST http://localhost:4000/auth/reset-request \
  -H "Content-Type: application/json" \
  -d '{"email":"good@email.com"}'

# Must return: {"message":"Reset code sent to email."}
```

Then check **Mailtrap inbox** — you should see the reset email arrive.

### Step 6 — Verify reset code in DB
```bash
cd server-api
node -e "
const{PrismaClient}=require('@prisma/client');
const p=new PrismaClient();
p.user.findUnique({where:{email:'good@email.com'}})
.then(u=>{console.log('Code:',u.resetCode,'Expiry:',u.resetCodeExpiry);p.\$disconnect();});
"
# Must show a 6-digit code and a future expiry date
```

---

## 8. All Test Scripts Reference

| Script File | Platform | Use Case | Run From |
|-------------|----------|----------|----------|
| `client-admin/UC1_Login_Web_Test.py` | Web (Selenium) | UC1 Login | Terminal 3 |
| `client-admin/UC3_web_reset_password.py` | Web (Selenium) | UC3 Reset Password | Terminal 3 |
| `client-admin/UC4_edit_profile.py` | Web (Selenium) | UC4 Edit Profile | Terminal 3 |
| `client-mobile/UC1_Login_Mobile_Test.py` | Mobile (Appium) | UC1 Login | Terminal 4 |
| `client-mobile/UC3_mobile_reset_password.py` | Mobile (Appium) | UC3 Reset Password | Terminal 4 |
| `client-mobile/UC4_mobile_edit_profile.py` | Mobile (Appium) | UC4 Edit Profile | Terminal 4 |

---

## 9. Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `EADDRINUSE: port 4000` | Previous API server still running | `lsof -ti:4000 \| xargs kill -9` then `npm run dev` |
| `ERR_CONNECTION_REFUSED` | API or web server not running | Start both servers first (Step 5.1) |
| `zsh: command not found: adb` | Android SDK not in PATH | Add platform-tools to PATH (Step 3.6) |
| `SessionNotCreatedException` | Emulator not running or app not installed | Start emulator first, wait for it to boot fully |
| `ConnectionRefusedError on port 4723` | Appium not running | Open Terminal 3 → run `appium` |
| `ModuleNotFoundError: No module named 'selenium'` | Virtual environment not activated | Run `source .venv/bin/activate` first |
| `ModuleNotFoundError: No module named 'appium'` | Virtual environment not activated | Run `source .venv/bin/activate` first |
| `NoSuchElementException` in Appium | App on wrong screen | Navigate app to Login/Profile screen manually first |
| Google Maps error on emulator | Maps API key not available | Tap "Go To Home" to bypass |
| `{"message":"Reset code sent"}` but UC3 fails | Mailtrap credentials wrong | Re-check `SENDER_EMAIL` and `SENDER_EMAIL_PW` in .env |
| Tests skip because `ghost_user` email exists | Previous test created the user | Delete the user from Prisma Studio |
| Port 3000 already in use | Previous `npm run dev` still running | Kill it: `lsof -ti:3000 \| xargs kill -9` |
| Windows: `'source' is not recognized` | Wrong activation command | Use `.venv\Scripts\activate` on Windows |
| App resets between Appium tests | `no_reset=False` in options | Change to `no_reset=True` if you want to keep session |

---

## 10. Quick Commands Cheatsheet

```bash
# ── KILL PORTS ──────────────────────────────────────────────
lsof -ti:4000 | xargs kill -9          # Kill API server (macOS/Linux)
lsof -ti:3000 | xargs kill -9          # Kill web server (macOS/Linux)

# ── START SERVERS ───────────────────────────────────────────
cd server-api && npm run dev            # API on port 4000
cd client-admin && npm run dev          # Web on port 3000
appium                                  # Appium on port 4723

# ── VIRTUAL ENV ─────────────────────────────────────────────
source .venv/bin/activate               # macOS/Linux
.venv\Scripts\activate                  # Windows

# ── RUN WEB TESTS ───────────────────────────────────────────
python client-admin/UC1_Login_Web_Test.py
python client-admin/UC3_web_reset_password.py
python client-admin/UC4_edit_profile.py

# ── RUN MOBILE TESTS ────────────────────────────────────────
python client-mobile/UC1_Login_Mobile_Test.py
python client-mobile/UC3_mobile_reset_password.py
python client-mobile/UC4_mobile_edit_profile.py

# ── DATABASE ────────────────────────────────────────────────
cd server-api && npx prisma studio      # Open DB UI at localhost:5555

# List all users
node -e "const{PrismaClient}=require('@prisma/client');const p=new PrismaClient();p.user.findMany({select:{email:true,role:true}}).then(u=>{console.log(JSON.stringify(u,null,2));p.\$disconnect();})"

# Read reset code (for UC3 testing)
node -e "const{PrismaClient}=require('@prisma/client');const p=new PrismaClient();p.user.findUnique({where:{email:'good@email.com'}}).then(u=>{console.log('Code:',u.resetCode);p.\$disconnect();})"

# ── EMULATOR ────────────────────────────────────────────────
adb devices                             # List connected devices
adb shell pm list packages | grep adamarbain  # Confirm app is installed

# ── VERIFY MAILTRAP ─────────────────────────────────────────
curl -X POST http://localhost:4000/auth/reset-request \
  -H "Content-Type: application/json" \
  -d '{"email":"good@email.com"}'
# Expected: {"message":"Reset code sent to email."}
```

---

> 📌 **Remember:** For every test run, make sure the correct servers are running and the virtual environment is activated. Screenshots are saved automatically to the `UC*_screenshots/` folders next to each script.
