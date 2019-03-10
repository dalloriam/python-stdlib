from dalloriam.orc.error import ORCException

from typing import Any, Dict, List, Tuple

from http import HTTPStatus

import requests


_ORC_URL = "http://localhost:{port}"


class ORCClient:

    def __init__(self, port=33000, check_liveness=True):
        self._orc_url = _ORC_URL.format(port=port)
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
        try:
            self._request('GET', '/')
        except ORCException:
            return False
        return True

    @property
    def supported_actions(self) -> Dict[str, List[str]]:
        if not self._supported_actions:
            self._supported_actions = self._request('GET', '/manage/actions_available')

        return self._supported_actions

    def supports(self, action_tag: str) -> bool:
        module, action = self._parse_action_tag(action_tag)
        return module in self.supported_actions and action in self.supported_actions[module]

    def do(self, action_tag: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.supports(action_tag):
            raise ORCException(f'Unsupported action: {action_tag}')

        return self._request('POST', f'/{action_tag}', body=data or {})

    # === Keyval module shortcuts ===

    def __getitem__(self, item: str) -> Any:
        try:
            return self.do('keyval/get', {'key': item})['value']
        except ORCException:
            raise KeyError(item)

    def __setitem__(self, key: str, value: Any) -> None:
        self.do('keyval/set', {'key': key, 'val': value})

    def __delitem__(self, key: str) -> None:
        self.do('keyval/del', {'key': key})

    def __contains__(self, item: str) -> bool:
        # TODO: This is not super optimal, to improve once keyval support fast lookups.
        return item in self.do('keyval/list')['values']
