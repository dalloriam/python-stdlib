from flask import Flask, Response

from http import HTTPStatus

import json


class API:

    def __init__(self, host: str, port: int, debug: bool):
        self._host = host
        self._port = port
        self._debug = debug

        self._flask: Flask = Flask(__name__)

    def route(self, rule, **kwargs):
        def decorator(fn):
            def internal():
                try:
                    data = fn()
                    return Response(json.dumps(data), content_type='application/json')
                except Exception as e:
                    return Response(
                        json.dumps({'error': str(e)}),
                        status=HTTPStatus.INTERNAL_SERVER_ERROR,
                        content_type='application/json'
                    )

            return self._flask.route(rule, **kwargs)(internal)
        return decorator

    def start(self):
        self._flask.run(host=self._host, port=self._port, debug=self._debug)