from flask import Flask, jsonify, request

def live():
    app = Flask(__name__)
    app.config["DEBUG"] = True

    #Health Check
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "status": "ok",
            "message": "Backend Live..."
        })
    return app

if __name__ == "__main__":
    app = live()
    app.run(host="0.0.0.0", port=5000)