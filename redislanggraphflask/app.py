# app.py
from flask import Flask, request, jsonify
import uuid
from redis_client import enqueue_task, set_status, get_status, get_result

app = Flask(__name__)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    task_id = str(uuid.uuid4())

    task = {
        "task_id": task_id,
        "text": data["text"],
        "process": data["process"]
    }

    enqueue_task(task)
    set_status(task_id, "queued")

    return jsonify({"task_id": task_id, "status": "queued"})


@app.route("/status/<task_id>")
def status(task_id):
    status = get_status(task_id)
    result = get_result(task_id) if status == "completed" else None

    return jsonify({
        "task_id": task_id,
        "status": status,
        "result": result
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)