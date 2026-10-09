# 💰 BudgetApp (Full-Stack Edition)

> A full-stack personal finance application featuring task/expense tracking, custom groups, theme customization, and user authentication backed by a relational SQLite database.

🌐 **Live Front-End:** [https://ceejaystokes09-stack.github.io/BudgetApp.github.io/](https://ceejaystokes09-stack.github.io/BudgetApp.github.io/)  
📂 **Repository:** [https://github.com/ceejaystokes09-stack/BudgetApp.github.io/](https://github.com/ceejaystokes09-stack/BudgetApp.github.io/)

---

## 🏗️ Architecture & Data Model

The application uses a **React front-end** communicating with a **Flask REST API** to persist user data in an **SQLite** database.

- **Data Scoping:**
  - **Guest Session:** Scoped directly to the browser's Flask session ID.
  - **Authenticated Users:** Scoped permanently to the signed-in user account.
- **Relational Storage:** Groups, tasks, theme preferences, and user accounts are structured in separate relational SQL tables with foreign key constraints.
- **Automatic Data Migration:** Legacy browser `localStorage` records (groups, tasks, theme settings) are automatically imported into SQL records on app load and cleared from the client.
- **Schema Safety:** Rebuilds older schema tables automatically while protecting non-empty legacy tables from accidental data loss.

---

## 🛠️ Tech Stack

- **Front-End:** React, JavaScript (ES6+), CSS3
- **Back-End:** Python, Flask, Flask-Session
- **Database:** SQLite
- **Build Tool:** Vite

---

## 🚀 Local Development Setup

To run the application locally, start both the back-end API and front-end server in separate terminal windows.

### 1. Back-End Setup
From the project root directory, export a secret key and execute the backend runner:

```bash
export FLASK_SECRET_KEY="$(openssl rand -hex 32)"
./run-backend.sh
