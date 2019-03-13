from dalloriam.authentication.user import User

from tests.mocks.datastore import MockDatastore

from unittest import mock

import pytest


@pytest.fixture()
def mock_ds():
    ds = MockDatastore()
    with mock.patch('dalloriam.authentication.user.datastore', ds):
        yield ds

    User._client = None


def test_user_save_saves_user_to_datastore(mock_ds: MockDatastore) -> None:
    assert not mock_ds.contents
    u = User('some_id', permissions=['permission.a'], services={'telegram': {'key': 'val'}})
    u.save()

    assert mock_ds.contents.get('User:some_id') == {
        'permissions': ['permission.a'],
        'services': {'telegram': {'key': 'val'}}
    }


def test_user_save_updates_user_in_datastore(mock_ds: MockDatastore) -> None:
    mock_ds.contents = {
        'User:some_id': {
            'permissions': ['permission.a'],
            'services': {'telegram': {'key': 'val'}}
        }
    }
    u = User('some_id', permissions=['permission.b'], services={'hello': 'world'})
    u.save()

    assert mock_ds.contents.get('User:some_id') == {
        'permissions': ['permission.b'],
        'services': {'hello': 'world'}
    }


def test_user_serialized_returns_correct_format(mock_ds: MockDatastore) -> None:
    u = User('some_id', permissions=['permissions.a'], services={'hello': 'world'})

    assert u.serialized == {
        'id': 'some_id',
        'permissions': ['permissions.a'],
        'services': {
            'hello': 'world'
        }
    }
