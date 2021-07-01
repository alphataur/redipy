import asyncio
import aiofiles
import aiohttp

class Downloader:
    def __init__(self, pool_size=5):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.pool_size = pool_size
        self.running = False
        self.session = False
        self.close = False
        self.success = []
        self.failed = []

    def close(self, force=False):
        #gracefull exit
        if not force:
            self.close = True
        else:
            for future in self.workers:
                future.cancel()
            #submit report

    def errorify(self, uri, fpath, error):
        return {
                    "uri": uri,
                    "fpath": fpath,
                    "error": error,
                    "success": False
                }

    def successify(self, uri, fpath):
        return {
                    "uri": uri,
                    "fpath": fpath,
                    "error": False,
                    "success": True
                }
    async def start_session(self):
        self.session = await aiohttp.ClientSession()

    def add(self, uri, fpath):
        self.queue.put_nowait((uri, fpath))

    async def download(self, uri, fpath, retries=5):
        if not self.session:
            await self.start_session()
        try:
            async with self.session.get(uri) as resp:
                if resp.status == 200:
                    async with aiofiles.open(fpath, "wb") as f:
                        async for chunk in resp.content.iter_chunked(1024):
                            await f.write(chunk)
            return self.successify(uri, fpath)
        except Exception as error:
            if retries > 0:
                return self.download(uri, fpath, retries-1)
            else:
                return self.errorify(uri, fpath, error)

    async def worker(self):
        while not self.close:
            uri, fpath = await self.queue.get()
            result = await self.download(uri, fpath)
            if result["success"]:
                self.success.append(result)
            else:
                self.failed.append(result)

    def start(self):
        self.workers = asyncio.gather(*[asyncio.ensure_future(self.worker()) for i in range(self.pool_size)])
        self.loop.run_until_complete(self.workers)

handle = Downloader(pool_size=10)

