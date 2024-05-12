import requests
import json
import base64
import random
import time
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from ecdsa import SigningKey, SECP256k1

def register_mission_control(session, server_url, pairs, cert):
    """Registers mission control data via HTTP POST with multiple node pairs"""
    url = f"{server_url}/v1/registermissioncontrol"
    payload = {"pairs": pairs}
    headers = {'Content-Type': 'application/json'}
    start_time = time.time()
    response = session.post(url, headers=headers, data=json.dumps(payload), verify=cert)
    end_time = time.time() - start_time
    return end_time, response.status_code

def query_aggregated_mission_control(session, server_url, cert):
    """Queries aggregated mission control data via HTTP GET"""
    url = f"{server_url}/v1/queryaggregatedmissioncontrol"
    start_time = time.time()
    response = session.get(url, verify=cert)
    end_time = time.time() - start_time
    return end_time, response.status_code

def generate_random_node():
    """Generate a random node identifier"""
    private_key = SigningKey.generate(curve=SECP256k1)
    compressed_public_key = private_key.get_verifying_key().to_string("compressed")
    return base64.b64encode(compressed_public_key).decode("utf-8")

def generate_random_history():
    """Generate random history data"""
    # Get the current time
    current_time = int(time.time())

    # Define the range for one week (in seconds)
    one_week = 7 * 24 * 60 * 60

    # Generate random values within the one-week range
    fail_time = random.randint(current_time - one_week, current_time)
    success_time = random.randint(current_time - one_week, current_time)

    fail_amt_sat = random.randint(0, 10000)
    success_amt_sat = random.randint(0, 10000)

    return {
        "fail_time": fail_time,
        "fail_amt_sat": fail_amt_sat,
        "fail_amt_msat": fail_amt_sat * 1000,
        "success_time": success_time,
        "success_amt_sat": success_amt_sat,
        "success_amt_msat": success_amt_sat * 1000,
    }

def plot_response_times(register_times, query_times):
    plt.figure(figsize=(10, 5))
    plt.plot(register_times, label='Register Times', color='b')
    plt.plot(query_times, label='Query Times', color='r')
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (seconds)')
    plt.title(f'Response Times [REST] - Register Ops: {len(register_times)}, Query Ops: {len(query_times)}')
    plt.axhline(y=np.median(register_times), color='b', linestyle='-.', label=f'Register Median: {np.median(register_times):.2f}')
    plt.axhline(y=np.median(query_times), color='r', linestyle='-.', label=f'Query Median: {np.median(query_times):.2f}')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    cert = "<your_ec_tls_cert_path>"
    server_url = "https://localhost:8081"

    session = requests.Session()

    # Make an initial request to the server for establishing TLS handshake excluding it
    # from the performance results.
    query_aggregated_mission_control(session=session, server_url=server_url, cert=cert)

    num_requests, num_pairs = 100_000, 1
    register_times, query_times = [], []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(num_requests):
            if random.choice(['register', 'query']) == 'register':
                pairs = []
                for _ in range(num_pairs):
                    node_from = generate_random_node()
                    node_to = generate_random_node()
                    history = generate_random_history()
                    pairs.append({
                        "nodeFrom": node_from,
                        "nodeTo": node_to,
                        "history": history
                    })
                future = executor.submit(register_mission_control, session, server_url, pairs, cert)
                futures.append(('register', future))
            else:
                future = executor.submit(query_aggregated_mission_control, session, server_url, cert)
                futures.append(('query', future))


        for task_type, future in futures:
            result = future.result()
            if task_type == 'register':
                register_times.append(result[0])
            else:
                query_times.append(result[0])

    plot_response_times(register_times, query_times)

if __name__ == '__main__':
    main()
