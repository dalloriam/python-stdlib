from typing import Any, Dict


class MockClient:

    def __init__(self, ds):
        self._ds = ds

    def get(self, key: str) -> Dict[str, Any]:
        return self._ds.contents.get(key)

    def put(self, entity: 'MockEntity') -> None:
        self._ds.contents[entity._key] = entity._body

    def key(self, type: str, id: str) -> str:
        return f'{type}:{id}'


class MockEntity:

    def __init__(self, key: str):
        self._key = key
        self._body = {}

    def update(self, **kwargs) -> None:
        self._body.update(**kwargs)


class MockDatastore:

    def __init__(self):
        self.contents = {}

    def Client(self) -> MockClient:
        return MockClient(ds=self)

    def Entity(self, key) -> MockEntity:
        return MockEntity(key=key)
