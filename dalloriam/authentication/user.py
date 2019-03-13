from dalloriam.exceptions import AccessDenied

from dataclasses import dataclass, field

from google.cloud import datastore

from typing import Any, Dict, List, Tuple

import google.auth.transport.requests
import google.oauth2.id_token
import requests


FIREBASE_AUTH_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEY}"


@dataclass
class User:

    _client = None

    uid: str
    permissions: List[str] = field(default_factory=lambda: [])
    services: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})

    @staticmethod
    def _ds():
        if User._client is None:
            User._client = datastore.Client()
        return User._client

    def save(self) -> None:
        """
        Save the user info to the authentication provider.
        """
        entity = datastore.Entity(User._ds().key('User', self.uid))
        entity.update(**{'permissions': self.permissions, 'services': self.services})
        User._ds().put(entity)

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
        return User._ds().get(User._ds().key('User', user_id))

    @staticmethod
    def _create_default_user(user_id: str) -> Dict[str, Any]:
        entity = datastore.Entity(User._ds().key('User', user_id))
        default_info = {
            'permissions': [],
            'services': {}
        }
        entity.update(**default_info)
        User._ds().put(entity)
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
    def get_token(api_key: str, email: str, password: str) -> Tuple[str, Tuple[str, str]]:
        """
        Authenticate against firebase and get token & refresh.
        Args:
            api_key (str): The firebase API key.
            email (str): The user email.
            password (str): The user password.

        Returns:
            The user ID and the ID / refresh tokens.
        """
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        response = requests.post(FIREBASE_AUTH_URL.format(API_KEY=api_key), json=payload)
        data = response.json()

        user_id = data['localId']
        id_token = data['idToken']
        refresh_token = data['refreshToken']
        return user_id, (id_token, refresh_token)

    @staticmethod
    def from_token(token: str) -> 'User':
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
