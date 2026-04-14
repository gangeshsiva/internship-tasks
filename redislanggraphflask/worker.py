# worker.py
from redis_client import dequeue_task, set_status, set_result
from graph import app  

while True:
    task = dequeue_task()
    task_id = task["task_id"]

    try:
        set_status(task_id, "running")

        result = app.invoke({
            "text": task["text"],
            "process": task["process"]
        })

        set_result(task_id, result)
        set_status(task_id, "completed")

    except Exception as e:
        set_status(task_id, f"failed: {str(e)}")