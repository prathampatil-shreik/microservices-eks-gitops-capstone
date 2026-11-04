"""
Task processor — contains the logic for simulating background work.
Each task type has its own processing simulation.
The FAILURE_RATE environment variable controls how often tasks fail,
which is useful for testing monitoring and alerting.
"""
import time
import random
import logging

from config import config

logger = logging.getLogger(__name__)

# Simulated work descriptions per task type
TASK_DESCRIPTIONS = {
    "DATA_PROCESSING": "Aggregating and transforming dataset records",
    "REPORT_GENERATION": "Compiling report from data sources",
    "EMAIL_NOTIFICATION": "Sending notification emails to subscribers",
    "FILE_EXPORT": "Exporting records to CSV/JSON format",
    "CLEANUP": "Removing expired records and temporary files",
}


def process_task(task_id: int, task_type: str, title: str) -> dict:
    """
    Simulate processing a task.

    Returns a dict with:
      - success: bool
      - message: str
      - duration_seconds: float

    Raises an exception if the task should fail (controlled by FAILURE_RATE).
    """
    description = TASK_DESCRIPTIONS.get(task_type, "Processing task")
    logger.info(f"[task={task_id}] Starting: {description}")

    # Simulate variable processing time
    duration = random.uniform(
        config.MIN_PROCESSING_SECONDS,
        config.MAX_PROCESSING_SECONDS,
    )
    time.sleep(duration)

    # Randomly fail based on configured failure rate
    if random.random() < config.FAILURE_RATE:
        raise RuntimeError(
            f"Simulated failure for task {task_id} "
            f"(failure_rate={config.FAILURE_RATE})"
        )

    message = f"{description} completed in {duration:.1f}s"
    logger.info(f"[task={task_id}] {message}")
    return {"success": True, "message": message, "duration_seconds": duration}
