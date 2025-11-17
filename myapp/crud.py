from sqlalchemy import Boolean, Column, Integer, String, delete, update
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    city = Column(String)
    active = Column(Boolean, default=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def update_city(session, user_id: int, new_city: str) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise ValueError("User not found")

    user.city = new_city

    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_old_users(session, age_limit: int) -> int:
    stmt = update(User).where(User.age > age_limit).values(active=False)

    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount


async def delete_inactive(session) -> int:
    stmt = delete(User).where(User.active == False)

    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount
