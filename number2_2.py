import aiohttp

async def fetch_content():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://google.com') as resp:
            text = await resp.text()
            print('{:.70}...'.format(text))

asyncio.run(fetch_content())
