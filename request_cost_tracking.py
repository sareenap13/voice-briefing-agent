import csv
from pathlib import Path

OPENAI_INPUT_PRICE_PER_MILLION_TOKENS = 0.25
OPENAI_OUTPUT_PRICE_PER_MILLION_TOKENS = 2.00
ELEVENLABS_PRICE_PER_THOUSAND_CHARACTERS = 0.10

REQUEST_METRICS_LOG_PATH = Path("request_metrics_log.csv")

def calculate_openai_cost_dollars(input_token_count, output_token_count):
    return (
        input_token_count * OPENAI_INPUT_PRICE_PER_MILLION_TOKENS
        + output_token_count * OPENAI_OUTPUT_PRICE_PER_MILLION_TOKENS
    ) / 1_000_000

def calculate_elevenlabs_cost_dollars(spoken_text):
    return len(spoken_text) / 1000 * ELEVENLABS_PRICE_PER_THOUSAND_CHARACTERS

def append_request_metrics_to_log(request_metrics):
    log_file_already_exists = REQUEST_METRICS_LOG_PATH.exists()
    with REQUEST_METRICS_LOG_PATH.open("a", newline = "") as log_file:
        csv_writer = csv.DictWriter(log_file, fieldnames=request_metrics.keys())
        if not log_file_already_exists:
            csv_writer.writeheader()
        csv_writer.writerow(request_metrics)