import aiohttp_jinja2
import aiohttp_auth
from aiohttp import web
from functools import wraps


# The decorator redirects to the authentication page,
# if the user is not logged in

def auth_redirect(func):
    async def decorator(*args, **kwargs):
        try:
            answer = await func(*args, **kwargs)
        except web.HTTPForbidden:
            url = args[0].app.router['auth'].url_for()
            return web.HTTPFound(url)
        return answer
    return decorator

# Login/logout view

async def login(request):
    params = await request.post()
    login = params.get('login', None)
    password = params.get('password', None)
    login_key = 'user:' + login + ':password'

    if login and password:
        user_pass = await request.app['redis'].get(login_key)
        if user_pass and user_pass.decode() == password:
            await aiohttp_auth.auth.remember(request, login)
            url = request.app.router['index'].url_for()
            return web.HTTPFound(url)
    
    url = request.app.router['auth'].url_for()
    return web.HTTPFound(url)

@auth_redirect
@aiohttp_auth.auth.auth_required
async def logout(request):
    await aiohttp_auth.auth.forget(request)
    url = request.app.router['auth'].url_for()
    return web.HTTPFound(url)

# Auth, card and index view

async def auth(request):
    return aiohttp_jinja2.render_template('auth.html',
                                          request,
                                          {})

@auth_redirect
@aiohttp_auth.auth.auth_required
async def card_handler(request):
    params = await request.post()
    card = params.get('card', None)
    user = await aiohttp_auth.auth.get_auth(request)

    login = str(user)
    balance_key = 'user:' + login + ':balance'
    balance = await request.app['redis'].get(balance_key)
    balance = balance.decode()
    params = {'login':login, 'balance': balance, 'card': card}
    return aiohttp_jinja2.render_template('card.html',
                                          request,
                                          params)

@auth_redirect
@aiohttp_auth.auth.auth_required
async def index(request):
    user = await aiohttp_auth.auth.get_auth(request)

    login = str(user)
    balance_key = 'user:' + login + ':balance'
    balance = await request.app['redis'].get(balance_key)
    balance = balance.decode()
    params = {'login':login, 'balance': balance}
    return aiohttp_jinja2.render_template('index.html',
                                          request,
                                          params)

