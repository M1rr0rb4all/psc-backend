from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from psc_lookup import build_structure

app = Flask(__name__)
CORS(app)

@app.route("/api/ownership-tree", methods=["GET"])
def ownership_tree():
    company_number = request.args.get("company_number")
    if not company_number:
        return jsonify({"error": "Missing company_number"}), 400

    try:
        structure = build_structure(company_number)
        return jsonify(structure)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)