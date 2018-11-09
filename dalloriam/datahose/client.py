import requests


class DatahoseClient:

    """
    The DatahoseClient allows for easy interfacing with the cloud datahose.
    """

    def __init__(self, service_host: str, password: str) -> None:
        """
        Constructor
        Args:
            service_host (str): Datahose endpoint
            password (str): Datahose password.
        """
        self._push_url = service_host

        self._headers = {
            'Authorization': password
        }

    def push(self, key: str, data: dict, time: float = None) -> None:
        """
        Push an event to the datahose.
        Args:
            key (str): The event key.
            data (dict): The event data.
            time (float): The time at which the event occured.
        """
        data = {
            'key': key,
            'body': data
        }
        if time is not None:
            data['time'] = time

        resp = requests.post(self._push_url, json=data, headers=self._headers)

        if resp.status_code != 200:
            raise ValueError(resp.text)

    def notify(self, sender: str, message: str) -> None:
        """
        Send a notification via the datahose.
        Args:
            sender (str): Sender of the notification.
            message (str): Markdown-formatted message to send.
        """
        data = {
            'sender': sender,
            'message': message
        }
        self.push('notification', data=data)
