import asyncio
from app.core.database import create_tables, async_session
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy import select


async def seed_demo():
    await create_tables()
    async with async_session() as db:
        existing = await db.execute(select(User).where(User.email == "demo@lawgic.in"))
        if existing.scalar_one_or_none():
            print("Demo user already exists.")
            return

        demo = User(
            email="demo@lawgic.in",
            password_hash=hash_password("password123"),
            full_name="Demo User",
            phone="9999999999",
            user_type="client",
            is_active=True,
        )
        db.add(demo)
        await db.commit()
        print("Demo user created: demo@lawgic.in / password123")


if __name__ == "__main__":
    asyncio.run(seed_demo())
