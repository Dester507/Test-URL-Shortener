from motor.motor_asyncio import AsyncIOMotorClient

from config import Config


class DatabaseManager:

    def __init__(self, model: str):
        self.client = AsyncIOMotorClient(Config.MONGO_URL)
        self.model = model
        self.database = 'main'

    async def all(self):
        return [row async for row in self.client[self.database][self.model].find()]

    async def filer(self, data: dict, **kwargs):
        return [row async for row in self.client[self.database][self.model].find(data, **kwargs)]

    async def get(self, **kwargs):
        return await self.client[self.database][self.model].find_one(kwargs)

    async def insert(self, new_data: dict):
        return await self.client[self.database][self.model].insert_one(new_data)

    async def update(self, updated_data, **kwargs):
        return await self.client[self.database][self.model].update_many(kwargs, update={'$set': updated_data})

    async def delete(self, filter_data):
        return await self.client[self.database][self.model].delete_many(filter_data)
