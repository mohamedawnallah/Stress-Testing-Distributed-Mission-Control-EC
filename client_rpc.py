import grpc
import time
import random
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from ecdsa import SigningKey, SECP256k1
from external_coordinator_pb2_grpc import ExternalCoordinatorStub
from external_coordinator_pb2 import RegisterMissionControlRequest, QueryAggregatedMissionControlRequest, PairHistory, PairData


def get_secure_channel(target: str, cert:str):
    with open(cert, 'rb') as f:
        trusted_certs = f.read()
    credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
    return grpc.secure_channel(target, credentials)

def generate_random_node():
    private_key = SigningKey.generate(curve=SECP256k1)
    compressed_public_key = private_key.get_verifying_key().to_string("compressed")
    return compressed_public_key

def generate_random_history():
    # Get the current time
    current_time = int(time.time())

    # Define the range for one week (in seconds)
    one_week = 7 * 24 * 60 * 60

    # Generate random values within the one-week range
    fail_time = random.randint(current_time - one_week, current_time)
    success_time = random.randint(current_time - one_week, current_time)

    fail_amt_sat = random.randint(0, 10000)
    success_amt_sat = random.randint(0, 10000)

    return PairData(
        fail_time=fail_time,
        fail_amt_sat=fail_amt_sat,
        fail_amt_msat=fail_amt_sat * 1000,
        success_time=success_time,
        success_amt_sat=success_amt_sat,
        success_amt_msat=success_amt_sat * 1000,
    )

def register_mission_control(stub, pairs):
    start_time = time.time()
    request = RegisterMissionControlRequest(pairs=pairs)
    response = stub.RegisterMissionControl(request)
    end_time = time.time() - start_time
    return end_time, response

def query_aggregated_mission_control(stub):
    start_time = time.time()
    request = QueryAggregatedMissionControlRequest()
    response = stub.QueryAggregatedMissionControl(request)
    end_time = time.time() - start_time
    return end_time, response

def plot_response_times(register_times, query_times):
    plt.figure(figsize=(10, 5))
    plt.plot(register_times, label='Register Times', color='b')
    plt.plot(query_times, label='Query Times', color='r')
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (seconds)')
    plt.title(f'Response Times [gRPC] - Register Ops: {len(register_times)}, Query Ops: {len(query_times)}')
    plt.axhline(y=np.median(register_times), color='b', linestyle='-.', label=f'Register Median: {np.median(register_times):.2f}')
    plt.axhline(y=np.median(query_times), color='r', linestyle='-.', label=f'Query Median: {np.median(query_times):.2f}')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    cert = "<your_ec_tls_cert_path>"
    channel = get_secure_channel(target="localhost:50050", cert=cert)

    stub = ExternalCoordinatorStub(channel)

    # Make an initial request to the server for establishing TLS handshake excluding it
    # from the performance results.
    query_aggregated_mission_control(stub=stub)

    num_requests, num_pairs = 3, 1
    register_times, query_times = [], []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(num_requests):
            if random.choice(['register', 'query']) == 'register':
                pairs = []
                for _ in range(num_pairs):
                    node_from = generate_random_node()
                    node_to = generate_random_node()
                    history = generate_random_history()
                    pairs.append(PairHistory(node_from=node_from, node_to=node_to, history=history))
                future = executor.submit(register_mission_control, stub, pairs)
                futures.append(('register', future))
            else:
                future = executor.submit(query_aggregated_mission_control, stub)
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