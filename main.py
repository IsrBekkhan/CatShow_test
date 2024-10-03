from contextlib import asynccontextmanager
from typing import Annotated, List, Sequence, Optional

from fastapi import Depends, FastAPI, status, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal, Base, engine
import models
import schemas
from config import RESPONSES, create_data


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_db_session = AsyncSessionLocal()
    await create_data(async_db_session)  # добавление тестовых данных
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Cat Show App",
    summary="Документация API",
    description="""
    Онлайн выставка котят.
    API позволяeт добавить, получить, изменить, удалить информацию о котёнке.
    """,
    version="0.0.1",
    contact={
        "name": "Бекхан Исрапилов",
        "email": "israpal@bk.ru",
    },
)


# Database dependency
async def get_db_async_session():
    db_async_session: AsyncSession = AsyncSessionLocal()
    try:
        yield db_async_session
    finally:
        await db_async_session.aclose()


@app.get(
    "/api/breeds",
    summary="получить списка пород",
    response_description="Успешное получение списка пород",
    status_code=status.HTTP_200_OK,
    tags=["Породы"],
)
async def get_breeds(
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.Breeds:
    """
    Возвращает список всех пород котят

    """
    return await models.Cat.get_breeds(db_async_session)


@app.get(
    "/api/cats",
    summary="получить всех котят",
    response_description="Успешное получение всех котят",
    status_code=status.HTTP_200_OK,
    tags=["Котёнки"],
)
async def get_cats(
    breed: str | None = None,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> Sequence[schemas.CatBrief]:
    """
    Возвращает список всех котят.
    Можно отфильтровать возвращаемый список по определённой породе,
    передачей в строке URL параметр breed=<порода>.

    """
    return await models.Cat.get_cats(db_async_session, breed)


@app.get(
    "/api/cats/{cat_id}",
    summary="информация о котёнке",
    response_description="Успешное получение информации о котёнке",
    status_code=status.HTTP_200_OK,
    tags=["Котёнки"],
    responses=RESPONSES[status.HTTP_404_NOT_FOUND],
)
async def get_cat(
    cat_id: int,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.CatDetail:
    """
    Возвращает подробную информацию о котёнке по его ID

    """
    return await models.Cat.get_cat(db_async_session, cat_id)


@app.post(
    "/api/cats",
    summary="добавить информацию о котёнке",
    response_description="Успешное добавление информации о котёнке",
    status_code=status.HTTP_201_CREATED,
    tags=["Котёнки"],
)
async def add_cat(
    cat_form: schemas.CatForm,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.CatDetail:
    """
    Добавление информации о котёнке

    """
    return await models.Cat.add_cat(db_async_session, cat_form)


@app.patch(
    "/api/cats/{cat_id}",
    summary="изменение информации о котенке",
    response_description="Успешное изменение информации о котенке",
    status_code=status.HTTP_200_OK,
    tags=["Котёнки"],
    responses=RESPONSES[status.HTTP_404_NOT_FOUND],
)
async def change_cat(
    cat_id: int,
    cat_form: schemas.CatChangeForm,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.CatDetail:
    """
    Изменение информации о котенке по его ID.
    Изменяемые поля должны быть переданы в теле запроса

    """
    return await models.Cat.change_cat(db_async_session, cat_id, cat_form)


@app.delete(
    "/api/cats/{cat_id}",
    summary="удаление информации о котёнке",
    response_description="Успешное удаление информации о котёнке",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Котёнки"],
)
async def delete_cat(
    cat_id: int,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> None:
    """
    Удаляет информацию о котёнке из БД по его ID

    """
    return await models.Cat.delete_cat(db_async_session, cat_id)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Обработчик исключений HTTPException

    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def uvicorn_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик непредвиденных исключений

    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=str(exc),
    )
