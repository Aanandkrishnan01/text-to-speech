"""Logging utility for structured performance and event recording."""

from __future__ import annotations

import csv
import datetime
import os
import psutil

# Get repository root directory dynamically
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, "tts_logs")
CSV_PATH = os.path.join(LOG_DIR, "tts_events.csv")


def log_event(
    event: str,
    language: str = "",
    generation_time: float = 0.0,
    details: str = "",
) -> None:
    """Log an event with performance metrics to tts_logs/tts_events.csv."""
    try:
        # Create log directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)

        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Get CPU usage (with a short interval to get a baseline on the first call)
        cpu_pct = psutil.cpu_percent(interval=0.1)

        # Get Memory usage of current process in MB
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)

        # Check if CSV exists to write header
        file_exists = os.path.isfile(CSV_PATH)

        with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Timestamp",
                    "Event",
                    "CPU_Usage_Pct",
                    "Memory_Usage_MB",
                    "Language",
                    "Generation_Time_Sec",
                    "Details"
                ])
            writer.writerow([
                timestamp,
                event,
                f"{cpu_pct:.1f}",
                f"{memory_mb:.1f}",
                language,
                f"{generation_time:.3f}" if generation_time > 0 else "",
                details
            ])
    except Exception as e:
        print(f"Failed to log event {event}: {e}")
