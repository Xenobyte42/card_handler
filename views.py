import aiohttp_jinja2
from aiohttp import web

async def auth(request):
    return aiohttp_jinja2.render_template('auth.html',
                                          request,
                                          params)

async def card_handler(request):
    card = request.match_info.get('card')
    login = "Xenobyte"
    balance = 100
    params = {'login':login, 'balance': balance, 'card': card}
    return aiohttp_jinja2.render_template('card.html', request, params)

async def index(request):
    login = "Xenobyte"
    balance = 100
    params = {'login':login, 'balance': balance}
    return aiohttp_jinja2.render_template('index.html',
                                          request,
                                          params)
