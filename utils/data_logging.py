import json
from datetime import datetime
import matplotlib

def log_data(generator_type: str, generator_subtype: str):
    with open('log.json', 'r') as file:
        log_data = json.load(file)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_recording = {"generator_type" : generator_type, 
                     "generator_subtype" : generator_subtype, 
                     "time": current_time}
    log_data.get('generation_data').append(new_recording)
    with open('log.json', 'w') as file:
        json.dump(log_data, file, indent=4)

def clear_data():
    with open('log.json', 'r') as file:
        log_data = json.load(file)
    log_data = {"generation_data" : []}
    with open('log.json', 'w') as file:
        json.dump(log_data, file, indent=4)

def show_data():
    pass


if __name__ == "__main__":
    # Test logging
    clear_data()
    log_data("algo01", "calm")
    with open('log.json') as f:
        data = json.load(f)
        print(data)
