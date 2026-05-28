import asyncio
from sqlalchemy.future import select
from app.models import Role
from app.database import AsyncSessionLocal


async def create_roles():
    async with AsyncSessionLocal() as db:
        roles_to_create = [
            {"name": "admin", "description": "Администратор сайта"},
            {"name": "user", "description": "Обычный пользователь"},
            {"name": "manager", "description": "Менеджер"}
        ]

        for role_data in roles_to_create:
            result = await db.execute(select(Role).where(Role.name == role_data["name"]))
            role = result.scalar_one_or_none()
            if not role:
                new_role = Role(**role_data)
                db.add(new_role)
                print(f"Роль '{role_data['name']}' была создана!")

        await db.commit()
        print("Все роли созданы!")


if __name__ == "__main__":
    asyncio.run(create_roles())
