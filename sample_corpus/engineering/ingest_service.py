# Telemetry Ingest Service
DEFAULT_BATCH_TIMEOUT = 180
MAX_BATCH_SIZE = 512

def start_ingest_pipeline():
    print(f"Pipeline running with default batch timeout = {DEFAULT_BATCH_TIMEOUT} seconds")
