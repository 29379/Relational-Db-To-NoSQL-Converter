from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from database import create_connection, get_sqlalchemy_uri, OUTPUT_PATH, mongo_database
from create_erd import create_erd
from sql_to_json import sql_to_json
from one_to_one import one_to_one
from many_to_many import many_to_many

app = Flask(__name__)
CORS(app)


@app.route("/connect", methods=["GET"])
def connect_to_db():
    try:
        conn = create_connection()
        if conn:
            return jsonify({"message": "Connected to PostgreSQL successfully."}), 200
        else:
            return jsonify({"message": "Connection failed."}), 500
    finally:
        if conn:
            conn.close()


@app.route("/sql-to-json", methods=["GET"])
def convert_sql_to_json():
    conn = create_connection()
    try:
        return jsonify(sql_to_json(conn))
    finally:
        if conn:
            conn.close()


@app.route("/view-json", methods=["GET"])
def view_json():
    directory_path = os.getcwd()
    filename = "schema_details.json"
    return send_from_directory(directory_path, filename, as_attachment=True)


@app.route("/generate-erd", methods=["GET"])
def generate_and_view_erd():
    uri = get_sqlalchemy_uri()
    create_erd(uri, OUTPUT_PATH)
    directory_path = os.getcwd()
    return send_from_directory(directory_path, OUTPUT_PATH, as_attachment=True)


@app.route("/mongo-db", methods=["GET"])
def connect_to_mongo():
    db = mongo_database()
    return jsonify({"message": "Connected to MongoDB successfully."}), 200


@app.route("/handle-relationship", methods=["POST"])
def handle_relationship():
    data = request.json
    conn = create_connection()
    db = mongo_database()
    rel_choice = data.get("rel_choice")
    choice = data.get("choice")

    try:
        if choice == "1":
            result = one_to_one(conn, db, rel_choice)
            return (
                jsonify(
                    {"message": "One-to-One relationship handled.", "result": result}
                ),
                200,
            )
        elif choice == "2":
            result = many_to_many(conn, db, rel_choice)
            return (
                jsonify(
                    {
                        "message": "Many-to-Many relationship handled with deletion of junction tables.",
                        "result": result,
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Invalid choice."}), 400
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
