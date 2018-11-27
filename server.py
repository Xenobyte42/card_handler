import redis
import configparser
from aiohttp import web
from urls import setup_routes, setup_static_routes, setup_jinja
from middleware import setup_middleware


SECTION = "redis_config"
HOST_SECTION = "host"
PORT_SECTION = "port"
DB_SECTION = "db"


class ServerDatabase:

    def __init__(self, cfgpath):
        self._cfg_parser = configparser.ConfigParser()
        self._cfg_parser.read(cfgpath)

        self._host = self._cfg_parser[SECTION][HOST_SECTION]
        self._port = int(self._cfg_parser[SECTION][PORT_SECTION])
        self._db_id = int(self._cfg_parser[SECTION][DB_SECTION])

        self._redis = redis.Redis(host=self._host,
                                  port=self._port,
                                  db=self._db_id)

class WebServer:

    def __init__(self):
        self._app = web.Application()

    def setup_server(self):
        setup_jinja(self._app)
        setup_middleware(self._app)
        setup_static_routes(self._app)
        setup_routes(self._app)

    def run(self):
        web.run_app(self._app)


if __name__ == "__main__":
    server = WebServer()
    server.setup_server()
    server.run()
