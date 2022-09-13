from aiohttp import web

from trademark_finder.application import create_app
from trademark_finder.configuration import AppConfig

if __name__ == '__main__':
    config = AppConfig()
    web.run_app(create_app(config), port=config.port)
