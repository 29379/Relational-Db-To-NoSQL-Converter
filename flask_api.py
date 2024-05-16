from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from database import create_connection, get_sqlalchemy_uri, OUTPUT_PATH, mongo_database
from create_erd import create_erd
from sql_to_json import sql_to_json
from one_to_one import one_to_one
from many_to_many import many_to_many, findUserPromptChoices

app = Flask(__name__)
CORS(app)


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
    return send_from_directory(directory_path, OUTPUT_PATH, as_attachment=False)


@app.route("/get-relationship-details", methods=["GET"])
def get_relationship_details():
    conn = create_connection()
    db = mongo_database()
    choices = findUserPromptChoices(conn, db)
    return jsonify(choices)


@app.route("/handle-relationship", methods=["POST"])
def handle_relationship():
    data = request.json
    conn = create_connection()
    db = mongo_database()
    referencingType = data.get("referencingType")
    conversionType = data.get("conversionType")
    relationType = data.get("relationType")
    userChoices = data.get("userChoices")

    try:
        if conversionType == "ConversionType.ttb":
            one_to_one(conn, db, referencingType)
            return (
                jsonify(
                    {
                        "message": "Table to collection conversion handled.",
                        "success": True,
                    }
                ),
                200,
            )
        elif conversionType == "ConversionType.smart":
            if "RelationshipType.mtm" in relationType:
                many_to_many(conn, db, referencingType, userChoices)

            # if "RelationshipType.oto" in relationType:
            # TODO" one - to - one
            # if "RelationshipType.otm" in relationType:
            # TODO" one - to - many

            return (
                jsonify(
                    {
                        "message": "Smart conversion handled.",
                        "success": True,
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Invalid choice.", "success": False}), 400
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
