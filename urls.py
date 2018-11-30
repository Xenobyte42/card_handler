from views import index, card_handler, auth, login, logout


def setup_routes(app):
    """Setting up routing"""
    routes = [('*', '/', index, 'index'),
              ('*', '/auth', auth, 'auth'),
              ('*', '/login', login, 'login'),
              ('*', '/logout', logout, 'logout'),
              ('*', '/card', card_handler, 'card_handler'),
    ]

    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])


