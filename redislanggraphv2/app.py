# app.py
from flask import Flask, request, jsonify
import uuid
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def enqueue_task(queue,task):
    r.lpush(queue, json.dumps(task))   #pushes the new task to the first [task1] -> [task2,task1]

def dequeue_task(queue):
    if queue in [QUEUE1,QUEUE2]:
        task = r.brpop(queue)  # blocking pop  #pushes the first or oldest task outside the list and processes it
        return json.loads(task[1])       #(b'task_queue', b'{"task_id": "123", "text": "hello", "process": "nlp"}'

def dequeue_by_task_id(queue_name, task_id):
    tasks = r.lrange(queue_name, 0, -1)

    for task_bytes in tasks:
        task = json.loads(task_bytes)

        if task["task_id"] == task_id:
            r.lrem(queue_name, 1, task_bytes)  # remove 1 occurrence
            return task

    return None

def set_status(task_id, status):
    r.set(f"status:{task_id}", status)

def get_status(task_id):
    return r.get(f"status:{task_id}")

def set_result(task_id, result):
    r.set(f"result:{task_id}", json.dumps(result))

def get_result(task_id):
    res = r.get(f"result:{task_id}")
    return json.loads(res) if res else None

def wait_queue(queue_key):
    length = r.llen(queue_key) 
    waitlist=dict()
    if length > 0: 
        tasks = r.lrange(queue_key, 0, length-1) 
        print(f"Queue '{queue_key}' has {length} tasks:") 
        for i, task_bytes in enumerate(tasks): 
            task = json.loads(task_bytes)    #task_bytes  {"name": "task1"}
            task_id = f"{queue_key}:{i+1}"     # Position-based ID   from latest to oldest
            waitlist[i+1] = {task["task_id"]:task["process"]}
        print("wait queue")
        print(waitlist)
        return waitlist
    else: 
        return {"message":"Wait Queue is empty"}
    
def run_queue(queue_key):
    length = r.llen(queue_key) 
    runlist=dict()
    if length > 0: 
        tasks = r.lrange(queue_key, 0, length-1) 
        print(f"Queue '{queue_key}' has {length} tasks:") 
        for i, task_bytes in enumerate(tasks): 
            task = json.loads(task_bytes)    #task_bytes  {"name": "task1"}
            task_id = f"{queue_key}:{i+1}"     # Position-based ID   from latest to oldest
            runlist[i+1] = {task["task_id"]:task["process"]}
        print("run queue")
        print(runlist)
        return runlist
    else: 
        return {"message":"Run Queue is empty"}
    
def complete_queue(queue_key):
    length = r.llen(queue_key) 
    completelist=dict()
    if length > 0: 
        tasks = r.lrange(queue_key, 0, length-1) 
        print(f"Queue '{queue_key}' has {length} tasks:") 
        for i, task_bytes in enumerate(tasks): 
            task = json.loads(task_bytes)    #task_bytes  {"name": "task1"}
            task_id = f"{queue_key}:{i+1}"     # Position-based ID   from latest to oldest
            completelist[i+1] = {task["task_id"]:task["process"]}
        print("run queue")
        print(completelist)
        return completelist
    else: 
        return {"message":"Complete Queue is empty"}

app = Flask(__name__)

QUEUE1="task_queue"
QUEUE2="running_queue"
QUEUE3="completed_queue"

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    task_id = str(uuid.uuid4())

    task = {
        "task_id": task_id,
        "text": data["text"],
        "process": data["process"]
    }

    enqueue_task(QUEUE1,task)
    set_status(task_id, "queued")

    return jsonify({"task_id": task_id, "status": "queued"})


@app.route("/status/<task_id>")
def status(task_id):
    status = get_status(task_id)
    result = get_result(task_id) if status == "completed" else None
    
    if status == "completed" :
        r.delete(f"status:{task_id}", f"result:{task_id}")

    return jsonify({
        "task_id": task_id,
        "status": status,
        "result": result
    })

#api for waiting tasks 
@app.route("/waiting",methods=["GET"])
def waiting():
    queue_key = QUEUE1 # Your queue name 
    # Get all tasks in queue with indices (task IDs are list positions) 
    wait = jsonify(wait_queue(queue_key))
    return wait
    
 
#endpoint for inprogress tasks
@app.route("/inprogress",methods=["GET"])
def inprogress():
    queue_key = QUEUE2
    run = jsonify(run_queue(queue_key))
    return run


#api for finished task queue
@app.route("/completed",methods=["GET"])
def completed():
    queue_key = QUEUE3
    completed = jsonify(complete_queue(queue_key))
    return completed


if __name__ == "__main__":
    app.run(port=5000, debug=True)