import jinja2
import aiohttp_jinja2
from aiohttp import web
from views import index, card_handler


def setup_jinja(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./templates/'))

def setup_static_routes(app):
    app.router.add_static('/static/',
                          path='./static',
                          name='static')

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/{card}', card_handler)
    
