from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import delete, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
import schemas


class Cat(Base):
    __tablename__ = "cats"

    id: Mapped[int] = mapped_column(primary_key=True)
    color: Mapped[str] = mapped_column(String(length=50), nullable=False)
    age: Mapped[int]
    description: Mapped[str] = mapped_column(
        String(length=500), nullable=False, server_default=""
    )
    breed: Mapped[str] = mapped_column(String(length=50))

    @classmethod
    async def get_breeds(
            cls,
            db_async_session: AsyncSession,
    ) -> schemas.Breeds:
        result = await db_async_session.execute(
            select(Cat.breed).distinct()
        )
        return schemas.Breeds(breeds=result.scalars().all())

    @classmethod
    async def get_cats(
            cls,
            db_async_session: AsyncSession,
            breed: str = None,
    ) -> Sequence["Cat"]:

        if breed:
            query = select(Cat).where(Cat.breed == breed)
        else:
            query = select(Cat)

        result = await db_async_session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_cat(
            cls,
            db_async_session: AsyncSession,
            cat_id: int,
    ) -> "Cat":
        result = await db_async_session.execute(
            select(Cat).where(Cat.id == cat_id)
        )
        cat = result.scalars().one_or_none()

        if cat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cat with ID '%s' does not exist" % cat_id
            )
        return cat

    @classmethod
    async def add_cat(
            cls,
            db_async_session: AsyncSession,
            cat_schema: schemas.CatForm
    ) -> "Cat":
        new_cat = Cat(**cat_schema.model_dump())

        db_async_session.add(new_cat)
        await db_async_session.commit()

        return new_cat

    @classmethod
    async def change_cat(
            cls,
            db_async_session: AsyncSession,
            cat_id: int,
            cat_schema: schemas.CatChangeForm,
    ) -> "Cat":
        result = await db_async_session.execute(
            select(Cat).where(Cat.id == cat_id)
        )
        cat = result.scalars().one_or_none()

        if cat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cat with ID '%s' does not exist" % cat_id
            )

        if cat_schema.color:
            cat.color = cat_schema.color
        if cat_schema.age:
            cat.age = int(cat_schema.age)
        if cat_schema.description:
            cat.description = cat_schema.description
        if cat_schema.breed:
            cat.breed = cat_schema.breed

        await db_async_session.commit()
        return cat

    @classmethod
    async def delete_cat(
            cls,
            db_async_session: AsyncSession,
            cat_id: int,
    ) -> None:
        await db_async_session.execute(
            delete(Cat).where(Cat.id == cat_id)
        )
        await db_async_session.commit()
