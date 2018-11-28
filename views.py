import aiohttp_jinja2
import aiohttp_auth
from aiohttp import web
from functools import wraps


def auth_redirect(func):
    async def decorator(*args, **kwargs):
        try:
            answer = await func(*args, **kwargs)
        except:
            url = args[0].app.router['auth'].url_for()
            return web.HTTPFound(url)
        return answer
    return decorator

async def login(request):
    params = await request.post()
    login = params.get('login', None)
    password = params.get('password', None)
    login_key = 'user:' + login + ':password'

    if login and password:
        user_pass = await request.app['redis'].get(login_key)
        if user_pass.decode() == password:
            await aiohttp_auth.auth.remember(request, login)
            url = request.app.router['index'].url_for()
            return web.HTTPFound(url)
    
    url = request.app.router['auth'].url_for()
    return web.HTTPFound(url)

async def auth(request):
    return aiohttp_jinja2.render_template('auth.html',
                                          request,
                                          {})

@auth_redirect
@aiohttp_auth.auth.auth_required
async def card_handler(request):
    params = await request.post()
    card = params.get('card', None)
    login = "Xenobyte"
    balance = 100
    params = {'login':login, 'balance': balance, 'card': card}
    return aiohttp_jinja2.render_template('card.html', request, params)

@auth_redirect
@aiohttp_auth.auth.auth_required
async def index(request):
    print(request)
    login = "Xenobyte"
    balance = 100
    params = {'login':login, 'balance': balance}
    return aiohttp_jinja2.render_template('index.html',
                                          request,
                                          params)

@auth_redirect
@aiohttp_auth.auth.auth_required
async def logout(request):
    await aiohttp_auth.auth.forget(request)
    url = request.app.router['auth'].url_for()
    return web.HTTPFound(url)
