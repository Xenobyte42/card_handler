import aioredis
import configparser
from aiohttp_auth import auth
from os import urandom
from aiohttp import web
from settings import setup_static_routes, setup_jinja, on_shutdown
from urls import setup_routes
from middleware import setup_middleware
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage


SECTION = "redis_config"
HOST_SECTION = "host"
PORT_SECTION = "port"
DB_SECTION = "db"


class WebServer:

    def __init__(self, cfgpath):
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(cfgpath)

        self._host = cfg_parser[SECTION][HOST_SECTION]
        self._port = int(cfg_parser[SECTION][PORT_SECTION])
        self._db_id = int(cfg_parser[SECTION][DB_SECTION])

    async def make_app(self):
        self._redis = await aioredis.create_redis((self._host, self._port),
                                                  db=self._db_id)

        policy = auth.SessionTktAuthentication(urandom(32), 60,
                                               include_ip=True)

        middlewares = [session_middleware(RedisStorage(self._redis)),
                       auth.auth_middleware(policy)]

        self._app = web.Application(middlewares=middlewares)
        self._app['redis'] = self._redis
        self.setup_server()

        self._app.on_shutdown.append(on_shutdown)
        return self._app


    def setup_server(self):
        setup_middleware(self._app)
        setup_jinja(self._app)
        setup_static_routes(self._app)
        setup_routes(self._app)

    def run(self):
        web.run_app(self.make_app())


if __name__ == "__main__":
    server = WebServer('redis.cfg')
    server.run()
