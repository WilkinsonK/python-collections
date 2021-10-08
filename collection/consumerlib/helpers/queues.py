from asyncio.queues import PriorityQueue, QueueEmpty


class MessageQueue(PriorityQueue):
    """
    Subclass of PriorityQueue which is able to
    parse/prepare incoming messages.
    """

    async def apush(self, message, priority: int = 999):
        item = self._prepare_message(message, priority)
        await self.put(item)

    async def apull(self):
        _, message = await self.get()
        return message

    def pull(self):
        try:
            _, message = self.get_nowait()
        except QueueEmpty:
            return
        return message

    def _prepare_message(self, message, priority):
        return (priority, message)
