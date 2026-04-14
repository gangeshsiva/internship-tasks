# redis_client.py
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def enqueue_task(task):
    r.lpush("task_queue", json.dumps(task))   #pushes the new task to the first [task1] -> [task2,task1]

def dequeue_task():
    task = r.brpop("task_queue")  # blocking pop
    return json.loads(task[1])                #pushes the first or oldest task outside the list and processes it

def set_status(task_id, status):
    r.set(f"status:{task_id}", status)

def get_status(task_id):
    return r.get(f"status:{task_id}")

def set_result(task_id, result):
    r.set(f"result:{task_id}", json.dumps(result))

def get_result(task_id):
    res = r.get(f"result:{task_id}")
    return json.loads(res) if res else None