
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', 'Anonymous')
    text = 'Hello, ' + name
    # Здесь идёт некоторая дополнительная логика с async/await
    # ...
    return web.Response(text=text)

app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle)])

web.run_app(app)
