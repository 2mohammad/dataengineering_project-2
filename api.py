import requests
import argparse
import sys
import json

BASE_URL = "http://localhost:8000/api/public/v1"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhaXJieXRlLXNlcnZlciIsInN1YiI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImV4cCI6MTczMTYzNjM2NSwicm9sZXMiOlsiV09SS1NQQUNFX0VESVRPUiIsIk9SR0FOSVpBVElPTl9SVU5ORVIiLCJXT1JLU1BBQ0VfUkVBREVSIiwiT1JHQU5JWkFUSU9OX0VESVRPUiIsIldPUktTUEFDRV9BRE1JTiIsIldPUktTUEFDRV9SVU5ORVIiLCJFRElUT1IiLCJBVVRIRU5USUNBVEVEX1VTRVIiLCJPUkdBTklaQVRJT05fTUVNQkVSIiwiT1JHQU5JWkFUSU9OX1JFQURFUiIsIlJFQURFUiIsIkFETUlOIiwiT1JHQU5JWkFUSU9OX0FETUlOIl19._Vjnk47pOnjizfAmnzcXTuL9G9MJ8FuLENL9VorvbUI"
DEFAULT_CONNECTION_ID = "7a97481b-8e3c-4e3c-8bce-95345942a3dc"
DEFAULT_JOB_ID = "1"

HEADERS = {
    "authorization": f"Bearer {AUTH_TOKEN}",
    "accept": "application/json",
    "content-type": "application/json",
}

def make_request(method, endpoint, **kwargs):
    """Make a request to the Airbyte API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=HEADERS, **kwargs)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error during {method} request to {url}: {e}")
        return None

def get_health_check():
    """
    Do a health check on the Airbyte API
    http://localhost:8000/api/public/v1/health
    """
    response = make_request("GET", "/health")
    print("Health check response")
    print(response.text)

def get_connections_list():
    """
    Get a list of connections from the Airbyte API
    http://localhost:8000/api/public/v1/connections
    """
    response = make_request("GET", "/connections")
    print("Connections lists")
    connections = json.loads(response.text)
    print(json.dumps(connections, indent=2))

def trigger_sync_job(connection_id=DEFAULT_CONNECTION_ID):
    """
    Trigger a sync job for a connection
    http://localhost:8000/api/public/v1/jobs
    """
    payload = { "jobType": "sync" , "connectionId": connection_id }
    response = make_request("POST", "/jobs", json=payload)
    jobs = json.loads(response.text)
    print(json.dumps(jobs, indent=4))

def get_job_status(job_id):
    """
    Get the status of a job by ID
    http://localhost:8000/api/public/v1/jobs/1
    """
    endpoint = f"/jobs/{job_id}"
    response = make_request("GET", endpoint)

    print(f"Job status for Job ID: {job_id}")
    status = json.loads(response.text)
    print(json.dumps(status, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Airbyte API Client")

    parser.add_argument(
        "command",
        choices=["health", "connections", "sync_job", "job_status"],
        help="Command to execute"
    )
    parser.add_argument(
        "--connection-id",
        type=str,
        default=DEFAULT_CONNECTION_ID,
        help=f"Connection ID for sync_job (default: {DEFAULT_CONNECTION_ID})"
    )
    parser.add_argument(
        "--job-id",
        type=str,
        default=DEFAULT_JOB_ID,
        help="Job ID for job_status"
    )
    args = parser.parse_args()

    if args.command == "health":
        get_health_check()
    elif args.command == "connections":
        get_connections_list()
    elif args.command == "sync_job":
        trigger_sync_job(connection_id=args.connection_id)
    elif args.command == "job_status":
        get_job_status(job_id=args.job_id)
    else:
        sys.exit(1)
