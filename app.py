import math
import os
import secrets
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from flask import Flask, current_app, jsonify, request, session

from back_end_ import backend
from database import DEFAULT_DATABASE_PATH, connect_database, initialize_database


app = Flask(__name__, template_folder="my-react-app")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE"] = os.environ.get(
    "BUDGET_DATABASE_PATH", str(DEFAULT_DATABASE_PATH)
)
app.config["INITIALIZED_DATABASES"] = set()


@app.before_request
def ensure_database():
    database_path = str(Path(current_app.config["DATABASE"]).resolve())
    if database_path not in current_app.config["INITIALIZED_DATABASES"]:
        initialize_database(database_path)
        current_app.config["INITIALIZED_DATABASES"].add(database_path)


def get_connection():
    return connect_database(current_app.config["DATABASE"])


def get_owner_id():
    user_id = session.get("user_id")
    if user_id:
        return f"user:{user_id}"

    guest_id = session.get("guest_id")
    if not guest_id:
        guest_id = str(uuid.uuid4())
        session["guest_id"] = guest_id
    return f"guest:{guest_id}"


def get_json_object():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def valid_text(value, *, allow_empty=False):
    return isinstance(value, str) and (allow_empty or bool(value.strip()))


def valid_amount(value):
    if isinstance(value, bool):
        return None
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if math.isfinite(amount) and amount >= 0 else None


def response_error(message, status):
    return jsonify({"Error": message}), status


@app.post("/api/auth/login")
def login_acc():
    data = get_json_object()
    if not data:
        return response_error("Email and password are required.", 400)

    email = data.get("email")
    password = data.get("password")
    if not valid_text(email) or not valid_text(password):
        return response_error("Email and password are required.", 400)

    with closing(get_connection()) as connection:
        user = connection.execute(
            'SELECT "ID", "NAME", "PASS" FROM "Users" WHERE "EMAIL" = ?',
            (email.strip().lower(),),
        ).fetchone()

    if not user or not backend.verify_password(user["PASS"], password):
        return response_error("Invalid email or password.", 401)

    session.clear()
    session["user_id"] = user["ID"]
    session["Name"] = user["NAME"]
    session["Email"] = email.strip().lower()
    return jsonify({"Status": "Success"}), 200


@app.post("/api/auth/create-acc")
def create_account():
    data = get_json_object()
    if not data:
        return response_error("Name, email, and password are required.", 400)

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not all(valid_text(value) for value in (name, email, password)):
        return response_error("Name, email, and password are required.", 400)

    user_id = str(uuid.uuid4())
    normalized_email = email.strip().lower()
    try:
        with closing(get_connection()) as connection:
            with connection:
                connection.execute(
                    'INSERT INTO "Users" ("ID", "NAME", "EMAIL", "PASS") '
                    "VALUES (?, ?, ?, ?)",
                    (
                        user_id,
                        name.strip(),
                        normalized_email,
                        backend.hash_password(password),
                    ),
                )
    except sqlite3.IntegrityError:
        return response_error("An account with that email already exists.", 409)

    session.clear()
    session["user_id"] = user_id
    session["Name"] = name.strip()
    session["Email"] = normalized_email
    return jsonify({"Status": "Success"}), 201


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"Status": "Success"}), 200


@app.get("/api/details/user-details")
def send_usersdetails():
    response = jsonify(
        {
            "name": session.get("Name") or "Guest",
            "email": session.get("Email") or "guest",
            "isAuthenticated": bool(session.get("user_id")),
        }
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/data")
def get_workspace_data():
    owner_id = get_owner_id()
    with closing(get_connection()) as connection:
        groups = connection.execute(
            'SELECT "ID" AS id, "NAME" AS name, "PARENT_ID" AS parentId '
            'FROM "Groups" WHERE "OWNER_ID" = ? ORDER BY "CREATED_AT", "ID"',
            (owner_id,),
        ).fetchall()
        tasks = connection.execute(
            'SELECT "ID" AS id, "GROUP_ID" AS groupId, "NAME" AS name, '
            '"DESCRIPTION" AS description, "MAX_PRICE" AS maxPrice, '
            '"CURRENT_PRICE" AS currentPrice, "IS_COMPLETE" AS isComplete '
            'FROM "Tasks" WHERE "OWNER_ID" = ? ORDER BY "CREATED_AT", "ID"',
            (owner_id,),
        ).fetchall()
        settings = connection.execute(
            'SELECT "THEME" FROM "UserSettings" WHERE "OWNER_ID" = ?',
            (owner_id,),
        ).fetchone()

    return jsonify(
        {
            "groups": [dict(group) for group in groups],
            "tasks": [
                {**dict(task), "isComplete": bool(task["isComplete"])}
                for task in tasks
            ],
            "theme": settings["THEME"] if settings else "light",
        }
    )


@app.post("/api/data/groups")
def create_group():
    data = get_json_object()
    if not data or not valid_text(data.get("id")) or not valid_text(data.get("name")):
        return response_error("A group ID and name are required.", 400)

    owner_id = get_owner_id()
    group_id = data["id"].strip()
    name = data["name"].strip()
    parent_id = data.get("parentId")
    if parent_id is not None and not valid_text(parent_id):
        return response_error("The parent group is invalid.", 400)
    parent_id = parent_id.strip() if isinstance(parent_id, str) else None

    try:
        with closing(get_connection()) as connection:
            with connection:
                if parent_id and not connection.execute(
                    'SELECT 1 FROM "Groups" WHERE "OWNER_ID" = ? AND "ID" = ?',
                    (owner_id, parent_id),
                ).fetchone():
                    return response_error("The parent group does not exist.", 400)
                connection.execute(
                    'INSERT INTO "Groups" ("OWNER_ID", "ID", "NAME", "PARENT_ID") '
                    "VALUES (?, ?, ?, ?)",
                    (owner_id, group_id, name, parent_id or None),
                )
    except sqlite3.IntegrityError:
        return response_error("A group with that ID already exists.", 409)

    return jsonify(
        {"id": group_id, "name": name, "parentId": parent_id or None}
    ), 201


@app.post("/api/data/tasks")
def create_task():
    data = get_json_object()
    if not data:
        return response_error("Task details are required.", 400)

    task_id = data.get("id")
    group_id = data.get("groupId")
    name = data.get("name")
    description = data.get("description")
    max_price = valid_amount(data.get("maxPrice", 0))
    current_price = valid_amount(data.get("currentPrice", 0))
    is_complete = data.get("isComplete", data.get("isGroup", False))
    if (
        not valid_text(task_id)
        or not valid_text(group_id)
        or not valid_text(name)
        or not valid_text(description, allow_empty=True)
        or max_price is None
        or current_price is None
        or not isinstance(is_complete, bool)
    ):
        return response_error("Task details are invalid.", 400)

    owner_id = get_owner_id()
    try:
        with closing(get_connection()) as connection:
            with connection:
                connection.execute(
                    'INSERT INTO "Tasks" ("OWNER_ID", "ID", "GROUP_ID", "NAME", '
                    '"DESCRIPTION", "MAX_PRICE", "CURRENT_PRICE", "IS_COMPLETE") '
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        owner_id,
                        task_id.strip(),
                        group_id.strip(),
                        name.strip(),
                        description.strip(),
                        max_price,
                        current_price,
                        int(is_complete),
                    ),
                )
    except sqlite3.IntegrityError:
        return response_error(
            "The task ID is already in use or its group does not exist.", 409
        )

    return jsonify({"Status": "Success"}), 201


@app.put("/api/data/tasks/<task_id>")
def update_task(task_id):
    data = get_json_object()
    if not data:
        return response_error("Task details are required.", 400)

    name = data.get("name")
    description = data.get("description")
    max_price = valid_amount(data.get("maxPrice"))
    current_price = valid_amount(data.get("currentPrice"))
    is_complete = data.get("isComplete", data.get("isGroup"))
    if (
        not valid_text(name)
        or not valid_text(description, allow_empty=True)
        or max_price is None
        or current_price is None
        or not isinstance(is_complete, bool)
    ):
        return response_error("Task details are invalid.", 400)

    with closing(get_connection()) as connection:
        with connection:
            result = connection.execute(
                'UPDATE "Tasks" SET "NAME" = ?, "DESCRIPTION" = ?, '
                '"MAX_PRICE" = ?, "CURRENT_PRICE" = ?, "IS_COMPLETE" = ?, '
                '"UPDATED_AT" = CURRENT_TIMESTAMP '
                'WHERE "OWNER_ID" = ? AND "ID" = ?',
                (
                    name.strip(),
                    description.strip(),
                    max_price,
                    current_price,
                    int(is_complete),
                    get_owner_id(),
                    task_id,
                ),
            )
    if result.rowcount == 0:
        return response_error("Task not found.", 404)
    return jsonify({"Status": "Success"}), 200


@app.put("/api/data/settings")
def update_settings():
    data = get_json_object()
    theme = data.get("theme") if data else None
    if theme not in ("light", "dark"):
        return response_error("Theme must be 'light' or 'dark'.", 400)

    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                'INSERT INTO "UserSettings" ("OWNER_ID", "THEME") VALUES (?, ?) '
                'ON CONFLICT("OWNER_ID") DO UPDATE SET "THEME" = excluded."THEME"',
                (get_owner_id(), theme),
            )
    return jsonify({"Status": "Success"}), 200


@app.post("/api/data/import-local")
def import_local_data():
    data = get_json_object()
    if not data:
        return response_error("Legacy data must be provided as JSON.", 400)
    groups = data.get("groups", [])
    tasks = data.get("tasks", [])
    theme = data.get("theme")
    if not isinstance(groups, list) or not isinstance(tasks, list):
        return response_error("Legacy groups and tasks must be arrays.", 400)
    if theme is not None and theme not in ("light", "dark"):
        return response_error("Legacy theme is invalid.", 400)

    group_ids = set()
    parent_ids = {}
    for group in groups:
        if (
            not isinstance(group, dict)
            or not valid_text(group.get("id"))
            or not valid_text(group.get("name"))
        ):
            return response_error("Legacy group data is invalid.", 400)
        group_ids.add(group["id"])
        parent_id = group.get("parentId")
        if parent_id is not None and not valid_text(parent_id):
            return response_error("Legacy group data is invalid.", 400)
        parent_ids[group["id"]] = parent_id

    for group_id in group_ids:
        seen = set()
        current_id = group_id
        while current_id in parent_ids and parent_ids[current_id] is not None:
            if current_id in seen or parent_ids[current_id] == group_id:
                return response_error("Legacy group hierarchy contains a cycle.", 400)
            seen.add(current_id)
            current_id = parent_ids[current_id]

    for task in tasks:
        if (
            not isinstance(task, dict)
            or not valid_text(task.get("id"))
            or not valid_text(task.get("groupId"))
            or not valid_text(task.get("name"))
            or not valid_text(task.get("description"), allow_empty=True)
            or valid_amount(task.get("maxPrice", 0)) is None
            or valid_amount(task.get("currentPrice", 0)) is None
            or not isinstance(task.get("isComplete", task.get("isGroup", False)), bool)
        ):
            return response_error("Legacy task data is invalid.", 400)

    owner_id = get_owner_id()
    try:
        with closing(get_connection()) as connection:
            with connection:
                for group in groups:
                    parent_id = parent_ids[group["id"]]
                    if parent_id not in group_ids and parent_id is not None:
                        exists = connection.execute(
                            'SELECT 1 FROM "Groups" WHERE "OWNER_ID" = ? AND "ID" = ?',
                            (owner_id, parent_id),
                        ).fetchone()
                        if not exists:
                            parent_id = None
                    connection.execute(
                        'INSERT OR IGNORE INTO "Groups" '
                        '("OWNER_ID", "ID", "NAME", "PARENT_ID") VALUES (?, ?, ?, ?)',
                        (owner_id, group["id"], group["name"].strip(), parent_id),
                    )

                for task in tasks:
                    max_price = valid_amount(task.get("maxPrice", 0))
                    current_price = valid_amount(task.get("currentPrice", 0))
                    connection.execute(
                        'INSERT OR IGNORE INTO "Tasks" '
                        '("OWNER_ID", "ID", "GROUP_ID", "NAME", "DESCRIPTION", '
                        '"MAX_PRICE", "CURRENT_PRICE", "IS_COMPLETE") '
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            owner_id,
                            task["id"],
                            task["groupId"],
                            task["name"].strip(),
                            task["description"].strip(),
                            max_price,
                            current_price,
                            int(task.get("isComplete", task.get("isGroup", False))),
                        ),
                    )

                if theme:
                    connection.execute(
                        'INSERT OR IGNORE INTO "UserSettings" ("OWNER_ID", "THEME") '
                        "VALUES (?, ?)",
                        (owner_id, theme),
                    )
    except sqlite3.IntegrityError:
        return response_error(
            "Legacy tasks must refer to a group in this browser session.", 400
        )
    return jsonify({"Status": "Success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
