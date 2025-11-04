from flask import jsonify


def api_response(payload: dict | list, status_code: int = 200):
    return jsonify(payload), status_code
