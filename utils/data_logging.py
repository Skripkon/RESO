from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import datetime
import json


def log_data(log_path: str,
             generator_type: str,
             generator_subtype: str,
             time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    """
    Makes a new recording in 'log.json' file. Recieves path to 'log.json',
    generator type, generator subtype and time of the query (by default
    sets the time of the function call). 
    """
    new_recording = {"generator_type": generator_type,
                     "generator_subtype": generator_subtype,
                     "time": time}

    try:
        with open(log_path, 'r') as file:
            log_data = json.load(file)
        log_data.get('generation_data').append(new_recording)
    except FileNotFoundError:
        log_data = {'generation_data': [new_recording]}

    with open(log_path, 'w') as file:
        json.dump(log_data, file, indent=4)


def clear_data(log_path):
    """
    Clears the log file and sets it to default state.
    Recieves path to 'log.json' file.
    """
    with open(log_path, 'r') as file:
        log_data = json.load(file)
    log_data = {"generation_data": []}
    with open(log_path, 'w') as file:
        json.dump(log_data, file, indent=4)


def count_queries_per_generator(log_path):
    """
    Counts the number of queries per each generator type for the entire log.
    Recieves filepath to file 'log.json' and returns a dict in
    format {generator_type : count} 
    """
    with open(log_path, 'r') as file:
        log_data = json.load(file)
    generator_counts = Counter(record['generator_type']
                               for record in log_data['generation_data'])

    return generator_counts


def count_queries_per_day(log_path):
    """
    Counts the number of queries per each day for the last 30 days.
    Recieves filepath to file 'log.json' and returns a dict in
    format {time : count} 
    """
    with open(log_path, 'r') as file:
        log_data = json.load(file)

    query_counts = defaultdict(int)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)

    for record in log_data['generation_data']:
        query_time = datetime.datetime.strptime(
            record['time'], '%Y-%m-%d %H:%M:%S').date()
        if start_date <= query_time <= end_date:
            query_counts[query_time] += 1

    return query_counts


def show_data(log_path):
    """
    Shows two graphs based on the 'log.json' file. Receives path 
    to the 'log.json' file.
    """
    fig, axes = plt.subplots(1, 2)

    data = count_queries_per_generator(log_path)
    args = list(data.keys())
    vals = list(data.values())
    axes[0].bar(args, vals)
    axes[0].set_title("Query count by generator type")
    axes[0].set_xlabel("Generator type")
    axes[0].set_ylabel("Usages")

    data = count_queries_per_day(log_path)
    args = list(data.keys())
    vals = list(data.values())
    axes[1].bar(args, vals)
    axes[1].set_title("Activity for the last month")
    axes[1].set_xlabel("Date")
    axes[1].set_xticklabels(data, rotation=90)
    axes[1].set_ylabel("Usages")

    plt.show()


if __name__ == "__main__":
    log_path = 'utils/log.json'

    # WARNING: CLEARS PREVIOUS DATA IN log.json
    clear_data(log_path)

    # Test logging
    log_data(log_path, "algo01", "calm")

    # Won't be shown in second graph because it is older than 30 days
    log_data(log_path, "algo02", "fast", "2023-12-15 15:03:03")

    log_data(log_path, "algo03", "calm", "2024-01-24 17:03:03")
    log_data(log_path, "algo02", "fast", "2024-01-15 15:03:03")
    log_data(log_path, "algo01", "calm")

    with open(log_path) as f:
        data = json.load(f)
        print(data)

    show_data(log_path)
