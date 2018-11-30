# CardSeacrcher

API for searching cards from Scryfall Magic Card searching

# Dependencies

To start the server you need to have a `redis` database and running `redis-server`.

Python requirements:

- python3.5.x and more
- configparser
- aiohttp
- aioredis
- aiohttp_auth
- aiohttp_session
- aiohttp_jinja2
- jinja2
- urllib

# Usage

To start the web server for the first time, configure `config-file` redis.cfg:

`host`=database_hostname

`port`=database_port

`db`=database_number

To start server you must use `python3 server.py -i <host> -p <port> -c <config_file_path>`

# Database usage

All data in the database is stored on a strictly defined template:

`user:<login>:password` - user password;

`user:<login>:balance` - user balance;

`card:img_name>:img` - path to image source;

`card:<name>:users` - list of users who bought this card;

