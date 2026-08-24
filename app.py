import os

# Force Playwright to use browsers installed inside the Python environment
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from job_processor import process_job


app = Flask(__name__)


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No request data received."
            }), 400

        url = data.get(
            "url",
            ""
        ).strip()

        if not url:

            return jsonify({
                "success": False,
                "error": "Job URL is required."
            }), 400

        result = process_job(
            url
        )

        return jsonify(
            result
        )

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
