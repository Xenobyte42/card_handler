import jinja2
import aiohttp_jinja2
from aiohttp import web
from views import index, card_handler, auth, login, logout


def setup_jinja(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./templates/'))
    app['static_root_url'] = './static/'

def setup_static_routes(app):
    app.router.add_static('/static/',
                          path='./static',
                          name='static')

def setup_routes(app):
    routes = [('*', '/', index, 'index'),
              ('*', '/auth', auth, 'auth'),
              ('*', '/login', login, 'login'),
              ('*', '/logout', logout, 'logout'),
              ('*', '/card', card_handler, 'card_handler'),
             ]
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])


