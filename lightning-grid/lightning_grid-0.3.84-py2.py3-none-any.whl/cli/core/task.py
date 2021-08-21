from dataclasses import dataclass


@dataclass
class Task:
    task_id: str
    status: str
    task_type: str
    message: str
    error: str
    stream_logs_expire_at: str
