from dalloriam.orc.error import ORCException

from typing import Any, Dict, List, Tuple

from http import HTTPStatus

import requests


_ORC_URL = "http://{host}:{port}"


class ORCClient:

    """
    ORC Client interfaces with the ORC personal orchestrator.
    """

    def __init__(self, host: str = 'localhost', port: int = 33000, check_liveness: bool = True):
        """
        Constructor.
        Args:
            host (str): The host where ORC is running.
            port (int): The port where ORC is running.
            check_liveness (bool): Whether to check if ORC is alive when starting the client.
        """
        self._orc_url = _ORC_URL.format(host=host, port=port)
        self._supported_actions: Dict[str, List[str]] = {}

        if check_liveness and not self.is_alive:
            raise ORCException(f'Could not find ORC server at [{self._orc_url}].')

    @staticmethod
    def _parse_action_tag(action_tag: str) -> Tuple[str, str]:
        splitted = action_tag.split('/')
        if len(splitted) != 2:
            raise ORCException(f'Invalid action tag: {action_tag}')

        return splitted[0], splitted[1]

    def _request(self, method, endpoint, body=None) -> dict:
        resp = requests.request(method, self._orc_url + endpoint, json=body)

        resp_bod = resp.json()

        if resp.status_code != HTTPStatus.OK or 'error' in resp_bod:
            # Something unusual happened
            if resp_bod and 'error' in resp_bod:
                raise ORCException(resp_bod['error'])

            raise ORCException(f'Unexpected status: {resp.status_code}')

        return resp_bod

    @property
    def is_alive(self) -> bool:
        """
        Returns:
            Whether the ORC server could be found.
        """
        try:
            self._request('GET', '/')
        except ORCException:
            return False
        return True

    @property
    def supported_actions(self) -> Dict[str, List[str]]:
        """
        Returns:
            A dictionary of actions supported by the ORC server.
        """
        if not self._supported_actions:
            self._supported_actions = self._request('GET', '/manage/actions_available')

        return self._supported_actions

    def supports(self, action_tag: str) -> bool:
        """
        Checks if an action is supported.
        Args:
            action_tag (str): The action to validate.

        Returns:
            Whether the action is supported.
        """
        module, action = self._parse_action_tag(action_tag)
        return module in self.supported_actions and action in self.supported_actions[module]

    def do(self, action_tag: str, **data: Any) -> Dict[str, Any]:
        """
        Perform an action.
        Args:
            action_tag (str): The action to execute.
            **data (Dict[str, Any]): The arguments to send to the action.

        Returns:
            The return payload of the action.
        """
        if not self.supports(action_tag):
            raise ORCException(f'Unsupported action: {action_tag}')

        return self._request('POST', f'/{action_tag}', body=data or {})

    def __getattr__(self, item: str) -> Any:
        if item in {'do', 'supports', 'supported_actions', 'is_alive', '_request', '_parse_action_tag'}:
            return super().__getattribute__(item)

        fn = lambda **x: self.do(item.replace('_', '/'), **x)
        return fn
