from dalloriam.exceptions import AccessDenied

from dataclasses import dataclass, field

from google.cloud import datastore

from typing import Any, Dict, List

import google.auth.transport.requests
import google.oauth2.id_token


@dataclass
class User:

    _ds = datastore.Client()

    uid: str
    permissions: List[str] = field(default_factory=lambda: [])
    services: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})

    @property
    def serialized(self) -> Dict[str, Any]:
        """
        Serializes the user info.
        Returns:
            The serialized user.
        """
        return {
            'id': self.uid,
            'permissions': self.permissions,
            'services': self.services
        }

    @staticmethod
    def _try_get_user_info(user_id: str) -> Dict[str, Any]:
        return User._ds.get(User._ds.key('User', user_id))

    @staticmethod
    def _create_default_user(user_id: str) -> Dict[str, Any]:
        entity = datastore.Entity(User._ds.key('User', user_id))
        default_info = {
            'permissions': [],
            'services': {}
        }
        entity.update(**default_info)
        User._ds.put(entity)
        return default_info

    @staticmethod
    def from_uid(user_id: str) -> 'User':
        """
        Fetches the permissions and services from datastore, creating the user over there if required.
        Args:
            user_id (str): The ID of the user from firebase auth.

        Returns:
            The user object.
        """
        user_info = User._try_get_user_info(user_id)

        if user_info is None:
            # Create the user with default
            user_info = User._create_default_user(user_id)

        return User(uid=user_id, **user_info)

    @staticmethod
    def from_token(token: str, refresh_token: str = None) -> 'User':
        """
        Validate an auth token & return the claims. Can only be called in an HTTP context.
        Args:
            token (str): The token to validate.

        Returns:
            The user claims.
        """
        if not token:
            raise AccessDenied('Invalid Token')

        HTTP_REQUEST = google.auth.transport.requests.Request()
        try:
            claims = google.oauth2.id_token.verify_firebase_token(token, HTTP_REQUEST)
        except ValueError:
            raise AccessDenied("Token Expired")  # TODO: Add refresh

        if not claims:
            raise AccessDenied("Invalid Token")

        return User.from_uid(claims['user_id'])
