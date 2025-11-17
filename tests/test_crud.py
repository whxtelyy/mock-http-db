import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from zadanie.myapp.crud import (Base, User, deactivate_old_users,
                                delete_inactive, update_city)

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(
        engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_update_city(async_session):
    user = User(name="A", age=25, city="Ekaterinburg")
    async_session.add(user)
    await async_session.commit()
    updated = await update_city(async_session, user.id, "Moscow")
    assert updated.city == "Moscow"
    db_user = await async_session.get(User, user.id)
    assert db_user.city == "Moscow"


@pytest.mark.asyncio
async def test_deactivate_old_users(async_session):
    user1 = User(name="Sergey", age=20, city="Ekaterinburg", active=True)
    user2 = User(name="Sava", age=30, city="Ekaterinburg", active=True)
    user3 = User(name="Petuh", age=40, city="Moscow", active=True)
    async_session.add(user1)
    async_session.add(user2)
    async_session.add(user3)
    await async_session.commit()
    count = await deactivate_old_users(async_session, age_limit=25)
    assert count == 2
    result = await async_session.execute(select(User).where(User.active == False))
    rows = result.scalars().all()
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_delete_inactive(async_session):
    user1 = User(name="Sergey", age=20, city="Ekaterinburg", active=True)
    user2 = User(name="Sava", age=30, city="Ekaterinburg", active=False)
    user3 = User(name="Petuh", age=40, city="Moscow", active=False)
    async_session.add(user1)
    async_session.add(user2)
    async_session.add(user3)
    await async_session.commit()
    deleted = await delete_inactive(async_session)
    assert deleted == 2
    result = await async_session.execute(select(User))
    all_users = result.scalars().all()
    assert len(all_users) == 1
    assert all_users[0].active == True
