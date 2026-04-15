from flask import Flask, request, jsonify
from icdcpt import ICD_CPT_SCT_code

app = Flask(__name__)

@app.route("/", methods=["POST"])
def chronology():
    data = request.json
    text = data.get("text", "")
    coordinates = text["coordinates"]
    texts = text["texts"]

    output=ICD_CPT_SCT_code(texts, coordinates)

    return output 

if __name__ == "__main__":
    app.run(port=9012, debug=True)
