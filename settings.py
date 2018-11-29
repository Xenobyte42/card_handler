import jinja2
import aiohttp_jinja2


async def on_shutdown(app):
    app['redis'].close()
    await app['redis'].wait_closed()

def setup_jinja(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./templates/'))

def setup_static_routes(app):
    app.router.add_static('/static/',
                          path='./static',
                          name='static')
    app['static_root_url'] = './static/' 
