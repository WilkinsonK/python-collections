from asyncio.queues import LifoQueue, QueueEmpty


class MessageQueue(LifoQueue):

    async def apush(self, message):
        await self.put(message)

    async def apull(self):
        message = await self.get()
        return message

    def push(self, message):
        while not (self.maxsize > self.qsize() + 1):
            time.sleep(1.0)
        self.put_nowait(message)

    def pull(self):
        try:
            message = self.get_nowait()
        except QueueEmpty:
            return
        return message
