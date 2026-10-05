from flask import Flask, request, jsonify
from back_end_ import backend

app = Flask(__name__, template_folder="my-react-app")


def GenId():
    import uuid
    return str(uuid.uuid1())








@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/auth/login", methods=["OPTIONS"])
def handle_preflight_login():
    return "", 204


@app.post("/api/auth/login")
def login_acc():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    
    if not all(
        isinstance(value, str) and value.strip()
        for value in (email, password)
    ):
        return jsonify(
            {"Status": "Error", "Error": "Name, email, and password are required."}
        ), 201
    db = backend(
        db_file_name="DATA.db",
        table_name="Users",
        db_folder_name="Festival-data",
        EMAIL=email.strip().lower(),
        PASS=password,
    )
    
    if (db.verify_user(email_column="EMAIL", password_column="PASS")):
        return jsonify({"Status": "Success"}), 200
    
    else: 
        return jsonify({"Status": "Error", "Error": "Invalid Username or Password. lease try agian or Create an account."})
    
    
    

@app.route("/api/auth/create-acc", methods=["OPTIONS"])
def handle_preflight():
    return "", 204


@app.post("/api/auth/create-acc")
def create_account():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, email, password)
    ):
        return jsonify(
            {"Status": "Error", "Error": "Name, email, and password are required."}
        ), 201

    db = backend(
        db_file_name="DATA.db",
        table_name="Users",
        db_folder_name="Festival-data",
        NAME=name.strip(),
        EMAIL=email.strip().lower(),
        PASS=backend.hash_password(password),
        ID=GenId(),
    )

    schema = (
        '"ID" TEXT PRIMARY KEY, '
        '"NAME" TEXT NOT NULL, '
        '"EMAIL" TEXT NOT NULL UNIQUE, '
        '"PASS" TEXT NOT NULL'
    )
    if not db.create_table_safely(schema):
        return jsonify(
            {"Status": "Error", "Error": "Could not create the users table."}
        ), 201

    if db.data_exists("EMAIL", email.strip().lower()):
        return jsonify(
            {"Status": "Error", "Error": "An account with that email already exists."}
        ), 201

    if not db.add_to_db():
        return jsonify(
            {"Status": "Error", "Error": "Could not save the account."}
        ),201

    return jsonify(
        {"Status": "Success"}
    ), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
    
    
    