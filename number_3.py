from collections import namedtuple
import asyncio
import aiohttp

Service = namedtuple('Service', ('name', 'url', 'ip_attr'))

SERVICES = (
    Service('ipify', 'https://api.ipify.org?format=json', 'ip'),
    Service('ip-api', 'http://ip-api.com/json', 'query')
)


async def fetch_ip(session, service):
    async with session.get(service.url) as response:
        if response.status == 200:
            data = await response.json()
            return data[service.ip_attr]


async def asynchronous():
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch_ip(session, service)) for service in SERVICES]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if task.result() is not None:
                print(f"My IP address is: {task.result()}")
                break


ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(asynchronous())
