from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def chronology():
    data = request.json
    text = data.get("text", "")

    return jsonify({
        "message": "this message is from chronology page"
    })

if __name__ == "__main__":
    app.run(port=9012, debug=True)
