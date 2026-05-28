import asyncio
from sqlalchemy.future import select
from app.models import User, Role
from app.database import AsyncSessionLocal
from app.utils.security import hash_password


async def create_admin():
    async with AsyncSessionLocal() as db:
        # Получаем роль admin
        result = await db.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            print("Role 'admin' не найдена! Сначала создайте роли.")
            return

        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).where(User.email == "admin@email.com"))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            print("Admin уже был создан ранее!")
            return

        # Создаём пользователя
        admin_user = User(
            name="Admin",
            email="admin@email.com",
            hashed_password=hash_password("password"),
            role_id=admin_role.id,
            is_active=True,
            is_verified=True,
        )
        db.add(admin_user)
        await db.commit()
        print("Admin был создан!")


if __name__ == "__main__":
    asyncio.run(create_admin())
