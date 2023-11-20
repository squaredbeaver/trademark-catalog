from aiohttp import web

from app.application import create_application
from app.configuration import AppConfig

if __name__ == '__main__':
    config = AppConfig()
    application = create_application(config)
    web.run_app(application, port=config.port)
