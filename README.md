# Budget app backend

The React app stores groups, tasks, theme preferences, and account information in
SQLite through the Flask API. Guest data is scoped to the browser's Flask
session; signed-in data is scoped to the account. Groups and tasks are stored in
separate relational tables, with tasks referencing their group.

## Run locally

Start the backend and frontend in separate terminals from the project directory:

```bash
export FLASK_SECRET_KEY="$(openssl rand -hex 32)"
./run-backend.sh
```

```bash
./run-frontend.sh
```

Open the `Local` URL printed by Vite in the frontend terminal. Stop either server
with `Ctrl+C` in its terminal.

SQLite creates or updates the schema in `Festival-data/DATA.db` on startup.
Set `BUDGET_DATABASE_PATH` to use another database file. Existing groups, tasks,
and theme settings in browser local storage are imported into the current
session's SQL records on the next app load, then removed from local storage.
An empty table from the older groups schema is rebuilt automatically. If that
legacy table contains records, startup stops rather than discarding them.

Signed-in users can open the Account page from the name in the top navigation
and log out there or directly from the navigation.

Set `FLASK_SECRET_KEY` to a stable, private value for persistent sessions,
especially outside local development. The development fallback is generated at
startup and invalidates sessions when the backend restarts.
