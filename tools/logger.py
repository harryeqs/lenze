from pathlib import Path
from datetime import datetime

def get_latest_log_file(log_directory):
    """
    Get the latest log file from the specified directory.
    """
    log_files = list(Path(log_directory).glob('tmp_log_*.log'))
    if not log_files:
        return None
    
    # Extract datetime from filename and sort by it
    def extract_datetime(file_path):
        try:
            filename = file_path.stem  # Get the file name without the extension
            date_str = filename.replace('tmp_log_', '')
            return datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S')
        except ValueError:
            return datetime.min
    
    latest_log_file = max(log_files, key=extract_datetime)
    return latest_log_file

def log_to_latest_file(log_directory, log_entry):
    """
    Append a log entry to the latest log file in the specified directory.
    """
    latest_log_file = get_latest_log_file(log_directory)
    if latest_log_file:
        with open(latest_log_file, 'a') as file:
            file.write(log_entry + '\n')
        print(f"Logged to {latest_log_file}")
    else:
        print("No log files found in the directory.")