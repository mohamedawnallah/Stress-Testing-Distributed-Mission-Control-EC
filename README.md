# Project Setup Instructions

## Setting Up the Python Environment

To set up the Python environment for this project, follow these steps:

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Compiling Protocol Buffers

To compile the Protocol Buffers for the gRPC service, use the following command. Replace `<external_coordinator_proto_dir>` with the directory containing your `.proto` files and `<external_coordinator_proto_file_path>` with the path to your specific `.proto` file.

```bash
python -m grpc_tools.protoc \
--proto_path=<external_coordinator_proto_dir> \
--proto_path=./googleapis \
--python_out=. \
--grpc_python_out=. \
<external_coordinator_proto_file_path>
```

## Stress Testing

### Testing the gRPC Endpoint

To test the gRPC endpoint, run the provided Python client for the RPC interface:

```bash
python client_rpc.py
```

### Testing the gRPC REST Proxy Endpoint

For stress testing the RESTful API endpoint provided via the gRPC Gateway, use the following command:

```bash
python client_rest.py
```

## Notes

- Make sure to replace placeholders in the commands (like `<external_coordinator_proto_dir>`) with actual values specific to your project.
- Ensure that the `googleapis` directory is correctly set up and contains the necessary files for gRPC-Gateway functionalities.
- Always activate the virtual environment before running any Python scripts to ensure that dependencies are correctly managed.
