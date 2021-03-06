import argparse
from sys import argv
from os import urandom
from configparser import ConfigParser
from aiohttp import web
from aioredis import create_redis
from aiohttp_auth import auth
from aiohttp_session import session_middleware, setup
from aiohttp_session.redis_storage import RedisStorage

from urls import setup_routes
from middleware import setup_middleware
from settings import setup_static_routes, setup_jinja, on_shutdown


SECTION = 'redis_config'
HOST_SECTION = 'host'
PORT_SECTION = 'port'
DB_SECTION = 'db'


class WebServer:

    def __init__(self, params):
        cfg_parser = ConfigParser()
        cfg_parser.read(params.config)

        self._host = cfg_parser[SECTION][HOST_SECTION]
        self._port = int(cfg_parser[SECTION][PORT_SECTION])
        self._db_id = int(cfg_parser[SECTION][DB_SECTION])
        self._webhost = params.host
        self._webport = params.port

    async def _make_app(self):
        """Create a Web application, configure 
        authentication tokens, connect storage, 
        and configure the web application for
        the first time
        """
        self._redis = await create_redis((self._host, self._port),
                                         db=self._db_id)

        policy = auth.SessionTktAuthentication(urandom(32),
                                               3600,
                                               include_ip=True)

        middlewares = [session_middleware(RedisStorage(self._redis)),
                       auth.auth_middleware(policy)]

        self._app = web.Application(middlewares=middlewares)
        self._app['redis'] = self._redis

        self._setup_server()

        self._app.on_shutdown.append(on_shutdown)
        return self._app


    def _setup_server(self):
        """Setting up 404 and 500 request
        processing, routing, static processing
        """
        setup_middleware(self._app)
        setup_jinja(self._app)
        setup_static_routes(self._app)
        setup_routes(self._app)

    def run(self):
        """Function running web-server"""

        web.run_app(self._make_app(), host=self._webhost, port=self._webport)

def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a server parser')
    parser.add_argument(
        '-i',
        action='store',
        dest='host',
        type=str,
        default='0.0.0.0',
        help='Server host'
    )
    parser.add_argument(
        '-p',
        action='store',
        dest='port',
        type=int,
        default=8080,
        help='Sever port'
    )
    parser.add_argument(
        '-c',
        action='store',
        dest='config',
        type=str,
        default='redis.cfg',
        help='Redis config'
    )
    return parser.parse_args(args)

if __name__ == '__main__':
    params = parse_args(argv[1:])
    server = WebServer(params)
    server.run()
