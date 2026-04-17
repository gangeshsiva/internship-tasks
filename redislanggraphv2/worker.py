# worker.py
from app import dequeue_task, dequeue_by_task_id, set_status, set_result, clear_cache, enqueue_task
from graph import compiled_graph

QUEUE1 = "task_queue"
QUEUE2 = "run_queue"
QUEUE3 = "complete_queue"

def run_worker():
    while True:
        task = dequeue_task(QUEUE1)
        enqueue_task(QUEUE2, task)
        task_id = task["task_id"]

        try:
            set_status(task_id, "running")

            result = compiled_graph.invoke({
                "text": task["text"],
                "process": task["process"]
            })

            set_result(task_id, result)
            set_status(task_id, "completed")

            completed_task = dequeue_by_task_id(QUEUE2, task_id)
            enqueue_task(QUEUE3, completed_task)

        except Exception as e:
            set_status(task_id, f"failed: {str(e)}")


