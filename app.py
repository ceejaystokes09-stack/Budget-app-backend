from flask import Flask, request, jsonify

app = Flask(__name__, template_folder="my-react-app")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/auth/login", methods=["OPTIONS"])
def handle_preflight():
    return "", 204


@app.post("/api/auth/login")
def login_account():
    data = request.get_json(silent=True) or {}
    print(f"Received JSON from React: {data!r}", flush=True)
    return jsonify({"Status": "Success", "data": data}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)