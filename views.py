import aiohttp_jinja2
from aiohttp import web

async def auth(request):
    return aiohttp_jinja2.render_template('auth.html', request, {})

async def card_handler(request):
    card = request.match_info.get('card')
    return aiohttp_jinja2.render_template('card.html', request, {'card': card})

async def index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})
