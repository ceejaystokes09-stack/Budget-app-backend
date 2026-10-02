from flask import Flask, request, jsonify

app = Flask(__name__, template_folder="my-react-app")

@app.post("/api/auth/login")
def login_account():
    data = request.get_json()
    print(f"Received JSON from React: {data!r}", flush=True)
    return jsonify({"Status": "Success"}), 200