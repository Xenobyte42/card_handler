import jinja2
import aiohttp_jinja2


async def on_shutdown(app):
    """Safely close the database 
    when the server is stopped
    """
    app['redis'].close()
    await app['redis'].wait_closed()

def setup_jinja(app):
    """Set the path to search for page templates"""

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./templates/'))

def setup_static_routes(app):
    """Set the path to search for static files"""

    app.router.add_static('/static/',
                          path='./static',
                          name='static')
    app['static_root_url'] = './static/' 
