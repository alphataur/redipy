import asyncio
import aiofiles
import aiohttp
import glob
import json

class Downloader:
    def __init__(self, pool_size=5):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.pool_size = pool_size
        self.running = False
        self.session = False
        self._close = False
        self.success = []
        self.failed = []
        self.session = aiohttp.ClientSession()

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

    def add(self, uri, fpath):
        self.queue.put_nowait((uri, fpath))

    async def download(self, uri, fpath, retries=5):
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
        while not self._close:
            try:
                task = self.queue.get()
                uri, fpath  = await asyncio.wait_for(task, timeout=10)
                result = await self.download(uri, fpath)
                print(result)
            except asyncio.TimeoutError as te:
                print("worker is idle for too long... exiting", te)
                break
            except Exception as e:
                print("worker failed at", e)
                continue

    def consume(self, name):
        files = glob.glob(name)
        for f in files:
            with open(f, "r") as fhandle:
                data = json.load(fhandle)
                for datum in data["data"]:
                    self.add(datum["url"], datum["fpath"])

    def start(self):
        self.workers = asyncio.gather(*[self.worker() for i in range(self.pool_size)])
        self.loop.run_until_complete(self.workers)

handle = Downloader(pool_size=10)
handle.consume("eggs/dakini/*.json")
handle.start()
