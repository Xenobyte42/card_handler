import aioredis
import configparser
import aiohttp_auth
from os import urandom
from aiohttp import web
from urls import setup_routes, setup_static_routes, setup_jinja
from middleware import setup_middleware
from aiohttp_session import get_session, session_middleware
from aiohttp_session.redis_storage import RedisStorage


SECTION = "redis_config"
HOST_SECTION = "host"
PORT_SECTION = "port"
DB_SECTION = "db"


class WebServer:

    def __init__(self, cfgpath):
        self._cfg_parser = configparser.ConfigParser()
        self._cfg_parser.read(cfgpath)

        self._host = self._cfg_parser[SECTION][HOST_SECTION]
        self._port = int(self._cfg_parser[SECTION][PORT_SECTION])
        self._db_id = int(self._cfg_parser[SECTION][DB_SECTION])

    async def make_app(self):
        self._redis = await aioredis.create_redis((self._host, self._port), db=self._db_id)

        policy = aiohttp_auth.auth.SessionTktAuthentication(urandom(32), 60,
                                                            include_ip=True)

        middlewares = [session_middleware(RedisStorage(self._redis)),
                       aiohttp_auth.auth.auth_middleware(policy)]

        self._app = web.Application(middlewares=middlewares)
        self._app['redis'] = self._redis
        self.setup_server()
        return self._app


    def setup_server(self):
        setup_jinja(self._app)
        setup_middleware(self._app)
        setup_static_routes(self._app)
        setup_routes(self._app)

    def run(self):
        web.run_app(self.make_app())


if __name__ == "__main__":
    server = WebServer('redis.cfg')
    server.run()
