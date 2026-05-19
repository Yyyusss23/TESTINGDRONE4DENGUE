# TESTINGDRONE4DENGUE
---

## 📌 Commit Message Guidelines

To keep our Git history clean and easy to understand, we follow the **Conventional Commits** format.

### 🔧 Format

```
type(scope): short description
```

### 📦 Common Types

* `feat` → new feature
* `fix` → bug fix
* `docs` → documentation changes only
* `style` → formatting (no logic changes)
* `refactor` → code change without adding features or fixing bugs
* `test` → adding or updating tests
* `chore` → maintenance tasks (config, dependencies, build, etc.)

---

### ✅ Good Examples

```
feat(login): add user authentication
fix(api): handle null response error
docs(readme): update setup instructions
refactor(cart): simplify total calculation
```

---

### ❌ Bad Examples (don’t do this)

```
update code
fix bug
final version
stuff
changes
```

These are useless because nobody can tell what actually changed.

---

### 📏 Rules

* Keep the first line short and clear (max ~50 characters)
* Use **present tense** (e.g., “add”, not “added”)
* One commit = one logical change
* Avoid mixing multiple fixes/features in one commit
* Be descriptive, not lazy

---

### 
---

## 🧪 Test Script File Naming Convention (Selenium & Appium)

To keep test files organized and easy to trace back to use cases, we follow a **Use Case–based naming structure**.

### 📁 Format

```
UC<number>_<use_case_name>_<tool>.ext
```

### 🔧 Breakdown

* `UC<number>` → Use case ID (from requirement/spec)
* `<use_case_name>` → short, lowercase, underscore-separated description
* `<tool>` → testing framework used (`selenium` or `appium`)
* `.ext` → file extension (`.java`, `.py`, `.js`, etc.)

---

### ✅ Examples

#### Selenium scripts

```
UC3_reset_password_selenium.java
UC5_login_validation_selenium.py
UC7_add_to_cart_selenium.java
```

#### Appium scripts

```
UC3_reset_password_appium.java
UC2_user_registration_appium.java
UC6_checkout_flow_appium.js
```

---

### 📌 Rules (important)

* Always match file name with the **Use Case ID**
* Use lowercase and underscores only
* No spaces, no random camelCase, no vague names like `test1.java`
* One file = one use case test (don’t mix flows)
* Keep naming consistent across Selenium & Appium

---

### 🚨 Why this matters

If you don’t follow this, your test suite becomes untraceable:

* You won’t know which test maps to which requirement
* Debugging becomes guesswork
* Group members will overwrite each other’s work

---

If you want to level this up further, I can also help you design:

* folder structure for Selenium vs Appium
* test report naming
* Git branch naming convention

