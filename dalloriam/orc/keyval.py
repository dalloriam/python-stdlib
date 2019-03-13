from .client import ORCClient
from .error import ORCException

from typing import Any


class KeyValStore:
    """
    Wrapper around the ORC keyval module.
    """

    def __init__(self, client: ORCClient = None) -> None:
        """
        Constructor.
        Args:
            client (Optional[ORCClient]): The ORC client instance to use.
        """
        self._client = client or ORCClient()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a key from the keyval store, returning default if it is missing.
        Args:
            key (str): The key to fetch.
            default (Any): The default item to return if key does not exist.

        Returns:
            The key value or the default item.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, item: str) -> Any:
        try:
            return self._client.do('keyval/get', key=item)['value']
        except ORCException:
            raise KeyError(item)

    def __setitem__(self, key: str, value: Any) -> None:
        self._client.do('keyval/set', key=key, val=value)

    def __delitem__(self, key: str) -> None:
        self._client.do('keyval/del', key=key)

    def __contains__(self, item: str) -> bool:
        # TODO: This is not super optimal, to improve once keyval support fast lookups.
        return item in self._client.do('keyval/list')['values']
