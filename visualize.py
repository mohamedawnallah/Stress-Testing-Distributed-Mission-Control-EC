import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def plot_response_times(register_response_times, query_response_times, mc_entries_registered, mc_entries_per_register, register_failure_rate, query_failure_rate, api_type):
    """
    Plots the response times for register and query operations.

    Args:
        register_response_times (list): List of response times for register operations.
        query_response_times (list): List of response times for query operations.
        mc_entries_registered (int): Number of mission control entries registered.
        mc_entries_per_register (int): Number of entries per register request.
        register_failure_rate (float): Failure rate for register requests.
        query_failure_rate (float): Failure rate for query requests.
        api_type (str): Type of API ('REST' or 'gRPC').

    """
    fig = plt.figure(figsize=(10, 5))
    fig.canvas.manager.set_window_title(f'Response Times Plot [{api_type}]')

    total_ops = len(register_response_times) + len(query_response_times)
    register_label = f'Register Failure Rate: {register_failure_rate*100:.2f}%'
    query_label = f'Query Failure Rate: {query_failure_rate*100:.2f}%'
    
    plt.plot(register_response_times, label=register_label, color='b')
    plt.plot(query_response_times, label=query_label, color='r')
    
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (seconds)')
    plt.title(f'Response Times [{api_type}] - Total Ops: {total_ops}, Register Ops: {len(register_response_times)}, Query Ops: {len(query_response_times)}')
    plt.axhline(y=np.median(register_response_times), color='b', linestyle='-.', label=f'Register Median: {np.median(register_response_times):.2f}')
    plt.axhline(y=np.median(query_response_times), color='r', linestyle='-.', label=f'Query Median: {np.median(query_response_times):.2f}')
    plt.legend()
    plt.grid(True)
    plt.text(0.5, 0.95, f'MC Entries Registered: {mc_entries_registered}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.90, f'MC Entries per Register: {mc_entries_per_register}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.show()

def extract_api_type(file_name):
    """
    Extracts the API type from the file name.

    Args:
        file_name (str): The name of the file.

    Returns:
        str: The API type ('REST' or 'gRPC').
    """
    if file_name.startswith("rest"):
        return "REST"
    elif file_name.startswith("grpc"):
        return "gRPC"
    else:
        return "Unknown"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize.py <response_times_file>")
        sys.exit(1)

    FILE = sys.argv[1]
    API_TYPE = extract_api_type(os.path.basename(FILE))

    # Read the JSON file.
    with open(FILE, 'r') as file:
        data = json.load(file)

    # Extract the required fields.
    register_response_times = data['register_response_times']
    query_response_times = data['query_response_times']
    register_failure_rate = data['register_failure_rate']
    query_failure_rate = data['query_failure_rate']
    mc_entries_per_register = data['mc_entries_per_register']
    mc_entries_registered = data['mc_entries_registered']

    # Plot the response times.
    plot_response_times(register_response_times, query_response_times, mc_entries_registered, mc_entries_per_register, register_failure_rate, query_failure_rate, API_TYPE)
