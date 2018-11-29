import aiohttp_jinja2
import aiohttp_auth
import cards
import urllib
from aiohttp import web
from functools import wraps


#TODO: пробелы в именах файлов
#TODO: починить донаты

PIC_COST = 20
STATIC_PATH = './static/img/'

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

async def save_image(request, card_src, card):
    card_img = urllib.request.urlopen(card_src)
    local_path = STATIC_PATH + card + '.jpg'
    with open(local_path, 'wb') as f:
        f.write(card_img.read())
    request.app['redis'].set('card:' + card + ':img', local_path)

async def get_img_card(request, card):
    user = await aiohttp_auth.auth.get_auth(request)
    login = str(user)
    card_key = 'card:' + card + ':img'
    card_users_key = 'card:' + card + ':users'
    balance_key = 'user:' + login + ':balance'
    card_src = await request.app['redis'].get(card_key)

    # If the picture is already in the database
    if card_src:
        card_src = card_src.decode()
        user_len = await request.app['redis'].llen(card_users_key)
        card_users = await request.app['redis'].lrange(card_users_key, 0, user_len)
        print(card_users)
        if not card_users or login.encode() not in card_users:
            await request.app['redis'].lpush(card_users_key, login)
            await request.app['redis'].decrby(balance_key, PIC_COST)

        balance = await request.app['redis'].get(balance_key)
        balance = balance.decode()
    else:
        cardseeker = cards.CardSeeker(card)
        await cardseeker.request()

        try:
            card_src = cardseeker.get_img_src()
            card = cardseeker.get_name()
            await request.app['redis'].decrby(balance_key, PIC_COST)
            await save_image(request, card_src, card)
        except cards.CardNotFound:
            card_src = STATIC_PATH + 'not_found.jpg'
            card = 'No such card!'
        balance = await request.app['redis'].get(balance_key)
        balance = balance.decode()
    params = {'login':login, 'balance': balance,
              'card': card, 'src': card_src}
    return params

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
    params = await get_img_card(request, card)

    await aiohttp_auth.auth.remember(request, params['login'])
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
    await aiohttp_auth.auth.remember(request, login)
    return aiohttp_jinja2.render_template('index.html',
                                          request,
                                          params)

