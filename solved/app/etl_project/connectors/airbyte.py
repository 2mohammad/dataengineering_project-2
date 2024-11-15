import time
import requests
import base64
import logging


class AirbyteClient:
    def __init__(self, server_name: str, secret: str):
        self.server_name = server_name
        self.secret = secret
        self.headers = {
            "authorization": f"Bearer {self.secret}",
            "accept": "application/json",
            "content-type": "application/json",
        }
        logging.basicConfig(level=logging.INFO)

    def valid_connection(self) -> bool:
        """Check if connection is valid"""
        url = f"http://{self.server_name}:8000/api/public/v1/health"
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            return True
        else:
            raise Exception(
                f"Airbyte connection is not valid. Status code: {response.status_code}. Error message: {response.text}"
            )

    def trigger_sync(self, connection_id: str):
        """Trigger sync for a connection_id"""
        url = f"http://{self.server_name}:8000/api/public/v1/jobs"
        data = {"connectionId": connection_id, "jobType": "sync"}
        response = requests.post(url=url, json=data, headers=self.headers)
        job_id = response.json().get("jobId")
        job_status = response.json().get("status")

        while job_status == "running":
            sleep_seconds = 5
            logging.info(
                f"Job {job_id} is running. Checking job again in {sleep_seconds} seconds."
            )
            time.sleep(sleep_seconds)
            url = f"http://{self.server_name}:8000/api/public/v1/jobs/{job_id}"
            data = {"id": job_id}
            job_response = requests.post(url=url, headers=self.headers)
            job_status = job_response.json().get("status")
            if job_status == "failed":
                raise Exception(f"Job {job_id} has failed. {job_response.text}")
            elif job_status == "succeeded":
                logging.info(f"Job {job_id} has ran successfully.")
