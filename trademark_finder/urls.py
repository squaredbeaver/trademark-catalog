from aiohttp import web

from trademark_finder.handlers.find_exact_trademark import FindExactTrademarkHandler
from trademark_finder.handlers.find_similar_trademark import FindSimilarTrademarkHandler

urls: list[web.RouteDef] = [
    web.view('/find-exact-trademark', FindExactTrademarkHandler),
    web.view('/find-similar-trademarks', FindSimilarTrademarkHandler),
]
