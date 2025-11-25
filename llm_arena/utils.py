import time, uuid

def now_ms() -> int:
    return int(time.time() * 1000)

def new_run_id() -> str:
    return str(uuid.uuid4())
