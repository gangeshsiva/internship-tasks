from multiprocessing import Process
from worker import run_worker

NUM_WORKERS = 8

if __name__ == "__main__":
    processes = []

    for i in range(NUM_WORKERS):
        p = Process(target=run_worker)
        p.start()
        processes.append(p)
        print(f"Started worker {i+1}")

    # Optional: wait for all processes
    for p in processes:
        p.join()