from flask import Flask, request, jsonify
from agents_hrms.agent import root_agent

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Call Google ADK agent
    response = root_agent.r
    (user_message)


    return jsonify({
        "input": user_message,
        "response": response.text
    })

if __name__ == "__main__":
    app.run(debug=True)
