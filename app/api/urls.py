from aiohttp import web

from app.api.handlers.register_trademark import register_trademark
from app.api.handlers.search_trademark import search_trademark

urls: list[web.RouteDef] = [
    web.get('/trademark', search_trademark),
    web.post('/trademark', register_trademark),
]
