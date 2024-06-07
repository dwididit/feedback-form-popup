import unittest
import httpx
import asyncio
from main import app, DATABASE_URL, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create test engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class FeedbackTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()
        cls.client = httpx.AsyncClient(app=app, base_url="http://test")
        cls.loop.run_until_complete(cls.create_test_database())

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(cls.drop_test_database())
        cls.loop.run_until_complete(cls.client.aclose())
        cls.loop.run_until_complete(engine.dispose())

    @staticmethod
    async def create_test_database():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_test_database():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def test_create_feedback(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 3,
                "full_name": "John Doe",
                "email": "john.doe@example.com"
            })
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "Feedback submitted successfully"
            assert data["data"]["score"] == 3
            assert data["data"]["full_name"] == "John Doe"
            assert data["data"]["email"] == "john.doe@example.com"

        self.loop.run_until_complete(run_test())

    def test_get_feedback(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 5,
                "full_name": "Test User",
                "email": "testuser@example.com"
            })
            assert response.status_code == 200, response.text

            data = response.json()
            feedback_id = data["data"]["id"]

            response = await self.client.get(f"/feedback/{feedback_id}")
            assert response.status_code == 200, f"Error: {response.text}"
            data = response.json()
            assert data["data"]["full_name"] == "Test User"

        self.loop.run_until_complete(run_test())

    def test_get_feedback_by_id_not_found(self):
        async def run_test():
            response = await self.client.get("/feedback/999")
            assert response.status_code == 500, f"Error: {response.text}"
            data = response.json()
            assert data["code"] == 500
            assert data["message"] == "404: Feedback not found"

        self.loop.run_until_complete(run_test())

    def test_get_feedback_by_id(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 3,
                "full_name": "John Doe",
                "email": "john.doe@example.com"
            })
            assert response.status_code == 200, response.text
            data = response.json()
            feedback_id = data["data"]["id"]

            response = await self.client.get(f"/feedback/{feedback_id}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "Feedback retrieved successfully"
            assert data["data"]["score"] == 3
            assert data["data"]["full_name"] == "John Doe"
            assert data["data"]["email"] == "john.doe@example.com"

        self.loop.run_until_complete(run_test())

    def test_get_all_feedback(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 5,
                "full_name": "Test User",
                "email": "testuser@example.com"
            })
            assert response.status_code == 200, response.text

            response = await self.client.get("/feedback/")
            assert response.status_code == 200, f"Error: {response.text}"
            data = response.json()
            assert len(data["data"]) > 0

        self.loop.run_until_complete(run_test())

    def test_update_feedback_form(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 3,
                "full_name": "John Doe",
                "email": "john.doe@example.com"
            })
            assert response.status_code == 200, response.text
            data = response.json()
            feedback_id = data["data"]["id"]

            response = await self.client.put(f"/feedback/{feedback_id}", json={
                "score": 4,
                "full_name": "John Smith"
            })
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "Feedback updated successfully"
            assert data["data"]["score"] == 4
            assert data["data"]["full_name"] == "John Smith"

        self.loop.run_until_complete(run_test())

    def test_update_feedback_by_id_not_found(self):
        async def run_test():
            response = await self.client.put("/feedback/999", json={
                "score": 4,
                "full_name": "John Smith"
            })
            assert response.status_code == 500, response.text
            data = response.json()
            assert data["code"] == 500
            assert data["message"] == "404: Feedback not found"

        self.loop.run_until_complete(run_test())

    def test_delete_feedback(self):
        async def run_test():
            response = await self.client.post("/feedback/", json={
                "score": 3,
                "full_name": "John Doe",
                "email": "john.doe@example.com"
            })
            assert response.status_code == 200, response.text
            data = response.json()
            feedback_id = data["data"]["id"]

            response = await self.client.delete(f"/feedback/{feedback_id}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "Feedback deleted successfully"

            response = await self.client.get(f"/feedback/{feedback_id}")
            assert response.status_code == 500, f"Error: {response.text}"
            data = response.json()
            assert data["code"] == 500
            assert data["message"] == "404: Feedback not found"

        self.loop.run_until_complete(run_test())

    def test_delete_feedback_by_id_not_found(self):
        async def run_test():
            response = await self.client.delete("/feedback/999")
            assert response.status_code == 500, f"Error: {response.text}"
            data = response.json()
            assert data["code"] == 500
            assert data["message"] == "404: Feedback not found"

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
