from fastapi import status
from sqlalchemy import select

import models

fixtures = [
    {
        "color": "Черный",
        "age": 5,
        "description": "Черный котенок с синими галазами",
        "breed": "Британец",
    },
    {
        "color": "Серый",
        "age": 10,
        "description": "Вислоухий котенок окраса Blue Point",
        "breed": "Шотландец",
    },
    {
        "color": "белый",
        "age": 12,
        "description": "Котенок белого цвета прямоухий",
        "breed": "Сиамский",
    },
]


async def create_data(async_db_session):
    async with async_db_session.begin():
        result = await async_db_session.execute(
            select(models.Cat)
        )
        cats = result.scalars().all()

        if len(cats) == 0:
            new_cats = [models.Cat(**cat) for cat in fixtures]
            async_db_session.add_all(new_cats)
    await async_db_session.aclose()


RESPONSES = {
    status.HTTP_404_NOT_FOUND: {
        404: {
            "description": "Ошибка, возникающее при передаче в запросе id записей, которых не существует в БД",
        }
    },
}
