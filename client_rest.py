import os
import requests
import json
import base64
import random
import time
import concurrent.futures
from ecdsa import SigningKey, SECP256k1


def get_self_signed_session(cert: str):
    session = requests.Session()
    session.verify = cert
    return session

def get_trusted_ca_session():
    session = requests.Session()
    session.verify = True
    return session

def get_insecure_session():
    session = requests.Session()
    session.verify = False
    return session

def register_mission_control(session, server_url, pairs, request_num):
    """
    Registers mission control data via HTTP POST with multiple node pairs.

    Args:
        session (requests.Session): The HTTP session to use for the request.
        server_url (str): The server URL.
        pairs (list): List of node pairs to register.
        request_num (int): The request number for logging purposes.

    Returns:
        tuple: Response time and status code.
    """
    url = f"{server_url}/v1/register_mission_control"
    payload = {"pairs": pairs}
    headers = {'Content-Type': 'application/json'}
    start_time = time.time()
    response = session.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time() - start_time
    if request_num > 0:
        print(f"register_request_response_{request_num}")
    return end_time, response.status_code

def query_aggregated_mission_control(session, server_url, request_num):
    """
    Queries aggregated mission control data via HTTP GET.

    Args:
        session (requests.Session): The HTTP session to use for the request.
        server_url (str): The server URL.
        request_num (int): The request number for logging purposes.

    Returns:
        tuple: Response time and status code.
    """
    url = f"{server_url}/v1/query_aggregated_mission_control"
    start_time = time.time()
    response = session.get(url, stream=True)
    end_time = time.time() - start_time
    if response.status_code != 200:
        return end_time, response.status_code

    pairs = []
    try:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                pairs.extend(chunk['result']['pairs'])

        if request_num > 0:
            print(f"query_request_response_{request_num}")
    except Exception as e:
        print(f"Failed to process streaming response: {e}")
        return end_time, 500

    return end_time, 200

def generate_random_node():
    """
    Generates a random node identifier.

    Returns:
        str: A base64-encoded compressed public key representing the node.
    """
    private_key = SigningKey.generate(curve=SECP256k1)
    compressed_public_key = private_key.get_verifying_key().to_string("compressed")
    return base64.b64encode(compressed_public_key).decode("utf-8")

def generate_random_history():
    """
    Generates random history data for mission control.

    Returns:
        dict: Randomly generated history data.
    """
    current_time = int(time.time())
    one_week = 7 * 24 * 60 * 60

    fail_time = random.randint(current_time - one_week, current_time)
    success_time = random.randint(current_time - one_week, current_time)

    fail_amt_sat = random.randint(1, 10000)
    success_amt_sat = random.randint(1, 10000)

    return {
        "fail_time": fail_time,
        "fail_amt_sat": fail_amt_sat,
        "fail_amt_msat": fail_amt_sat * 1000,
        "success_time": success_time,
        "success_amt_sat": success_amt_sat,
        "success_amt_msat": success_amt_sat * 1000,
    }

def save_data_to_json(register_response_times, query_response_times, register_failure_rate, query_failure_rate, mc_entries_registered, mc_entries_per_register, directory="data", filename="rest_response_times.json"):
    """
    Saves response times and failure rates to a JSON file.

    Args:
        register_response_times (list): List of register request response times.
        query_response_times (list): List of query request response times.
        register_failure_rate (float): Failure rate for register requests.
        query_failure_rate (float): Failure rate for query requests.
        mc_entries_registered (int): Number of mission control entries registered.
        mc_entries_per_register (int): Number of entries per register request.
        directory (str): Directory to save the file in.
        filename (str): Name of the JSON file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)

    data = {
        "register_response_times": register_response_times,
        "query_response_times": query_response_times,
        "register_failure_rate": register_failure_rate,
        "query_failure_rate": query_failure_rate,
        "mc_entries_per_register": mc_entries_per_register,
        "mc_entries_registered": mc_entries_registered,
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filepath}")

def main():
    """
    Main function to perform RESTful register and query operations and save the results.
    """
    server_url = "https://<your_ec_domain>:8081"
    session = get_trusted_ca_session()

    num_requests, mc_entries_per_register = 12, 3
    register_response_times, query_response_times = [], []
    register_failed_requests, query_failed_requests = 0, 0
    tasks = []

    # Generate pairs and prepare tasks.
    for request in range(num_requests):
        print("Preparing request:", request+1)
        if random.choice(['register', 'query']) == 'register':
            pairs = []
            for _ in range(mc_entries_per_register):
                node_from = generate_random_node()
                node_to = generate_random_node()
                history = generate_random_history()
                pairs.append({
                    "nodeFrom": node_from,
                    "nodeTo": node_to,
                    "history": history
                })
            tasks.append(('register', session, server_url, pairs, request+1))
        else:
            tasks.append(('query', session, server_url, request+1))

    # Submit all tasks at once.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for task in tasks:
            if task[0] == 'register':
                future = executor.submit(register_mission_control, task[1], task[2], task[3], task[4])
                futures.append(('register', future))
            else:
                future = executor.submit(query_aggregated_mission_control, task[1], task[2], task[3])
                futures.append(('query', future))

        print(f"All {num_requests} requests sent in parallel!")

        for task_type, future in futures:
            result = future.result()
            if task_type == 'register':
                register_response_times.append(result[0])
                if result[1] is None:
                    register_failed_requests += 1
            else:
                query_response_times.append(result[0])
                if result[1] == 500:
                    query_failed_requests += 1

    register_failure_rate = register_failed_requests / len(register_response_times)
    query_failure_rate = query_failed_requests / len(query_response_times)
    mc_entries_registered = len(register_response_times) * mc_entries_per_register
    print(f"Total Register Requests: {len(register_response_times)}, Failed Register Requests: {register_failed_requests}, Register Failure Rate: {register_failure_rate:.4f}")
    print(f"Total Query Requests: {len(query_response_times)}, Failed Query Requests: {query_failed_requests}, Query Failure Rate: {query_failure_rate:.4f}")
    print(f"Mission Contorl Entries Registered: {mc_entries_registered}")
    print(f"Mission Contorl Entries per Register: {mc_entries_per_register}")

    # Save data to JSON file.
    save_data_to_json(
        register_response_times=register_response_times, query_response_times=query_response_times, register_failure_rate=register_failure_rate,
        query_failure_rate=query_failure_rate, mc_entries_registered=mc_entries_registered, mc_entries_per_register=mc_entries_per_register
    )

if __name__ == '__main__':
    main()
