import os
import grpc
import time
import random
import concurrent.futures
import json
from ecdsa import SigningKey, SECP256k1
from external_coordinator_pb2_grpc import ExternalCoordinatorStub
from external_coordinator_pb2 import RegisterMissionControlRequest, QueryAggregatedMissionControlRequest, PairHistory, PairData

def get_self_signed_channel(target: str, cert: str):
    """
    Creates a secure gRPC channel using a self-signed certificate.

    Args:
        target (str): The server address (e.g., 'localhost:50051').
        cert (str): Path to the self-signed certificate file.

    Returns:
        grpc.Channel: A secure gRPC channel.
    """
    with open(cert, 'rb') as f:
        trusted_certs = f.read()
    credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
    return grpc.secure_channel(target, credentials)

def get_trusted_ca_channel(target: str):
    """
    Creates a secure gRPC channel using certificates from a trusted CA.

    Args:
        target (str): The server address (e.g., 'example.com:50051').

    Returns:
        grpc.Channel: A secure gRPC channel.
    """
    # Use default system-trusted CA certificates
    credentials = grpc.ssl_channel_credentials()
    return grpc.secure_channel(target, credentials)

def generate_random_node():
    """
    Generates a random node identifier using ECDSA.

    Returns:
        bytes: A compressed public key representing the node.
    """
    private_key = SigningKey.generate(curve=SECP256k1)
    compressed_public_key = private_key.get_verifying_key().to_string("compressed")
    return compressed_public_key

def generate_random_history():
    """
    Generates random history data for mission control.

    Returns:
        PairData: Randomly generated PairData object.
    """
    current_time = int(time.time())
    one_week = 7 * 24 * 60 * 60

    fail_time = random.randint(current_time - one_week, current_time)
    success_time = random.randint(current_time - one_week, current_time)

    fail_amt_sat = random.randint(1, 10000)
    success_amt_sat = random.randint(1, 10000)

    return PairData(
        fail_time=fail_time,
        fail_amt_sat=fail_amt_sat,
        fail_amt_msat=fail_amt_sat * 1000,
        success_time=success_time,
        success_amt_sat=success_amt_sat,
        success_amt_msat=success_amt_sat * 1000,
    )

def register_mission_control(stub, pairs, request_num):
    """
    Sends a RegisterMissionControlRequest to the server.

    Args:
        stub (ExternalCoordinatorStub): The gRPC stub for the External Coordinator service.
        pairs (list): List of PairHistory objects to register.
        request_num (int): The request number for logging purposes.

    Returns:
        tuple: Response time and the server response.
    """
    start_time = time.time()
    request = RegisterMissionControlRequest(pairs=pairs)
    response = stub.RegisterMissionControl(request)
    end_time = time.time() - start_time
    if request_num > 0:
        print(f"register_request_response_{request_num}: {end_time:0.2f}")
    return end_time, response

def query_aggregated_mission_control(stub, request_num):
    """
    Sends a QueryAggregatedMissionControlRequest to the server.

    Args:
        stub (ExternalCoordinatorStub): The gRPC stub for the External Coordinator service.
        request_num (int): The request number for logging purposes.

    Returns:
        tuple: Response time and status code.
    """
    start_time = time.time()
    request = QueryAggregatedMissionControlRequest()
    pairs = []
    try:
        for response in stub.QueryAggregatedMissionControl(request):
            pairs.extend(response.pairs)
    except Exception as e:
        print(f"Failed to process streaming response: {e}")
        end_time = time.time() - start_time
        return end_time, 500

    end_time = time.time() - start_time
    if request_num > 0:
        print(f"query_request_response_{request_num}: {end_time:0.2f}")
    return end_time, 200

def save_data_to_json(register_response_times, query_response_times, register_failure_rate, query_failure_rate,
                      mc_entries_registered, mc_entries_per_register, directory="data", filename="grpc_response_times.json"):
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
    Main function to perform gRPC register and query operations and save the results.
    """
    server_url = "<your_ec_domain>:50050"
    channel = get_trusted_ca_channel(server_url)

    stub = ExternalCoordinatorStub(channel)

    # Make an initial request to the server for establishing TLS handshake excluding it
    # from the performance results.
    print("Making 1st request for TLS handshake!")
    query_aggregated_mission_control(stub=stub, request_num=0)

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
                pairs.append(PairHistory(node_from=node_from, node_to=node_to, history=history))
            tasks.append(('register', stub, pairs, request+1))
        else:
            tasks.append(('query', stub, request + 1))

    # Submit all tasks at once.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for task in tasks:
            if task[0] == 'register':
                future = executor.submit(register_mission_control, task[1], task[2], task[3])
                futures.append(('register', future))
            else:
                future = executor.submit(query_aggregated_mission_control, task[1], task[2])
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

    # Save data to JSON file.
    save_data_to_json(
        register_response_times=register_response_times, query_response_times=query_response_times, register_failure_rate=register_failure_rate,
        query_failure_rate=query_failure_rate, mc_entries_registered=mc_entries_registered, mc_entries_per_register=mc_entries_per_register,
    )

if __name__ == '__main__':
    main()
