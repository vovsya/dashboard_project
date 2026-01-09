from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
import asyncio
from dashboard_app.dashboard.security.auth import get_current_user
from sqlalchemy import text
from dashboard_app.dashboard.db.db_engine import engine
from dashboard_app.dashboard.utils.apicalls import get_weather, get_currencies
from datetime import date
import random


pages_router = APIRouter(prefix="/pages", tags=["Страницы"])


@pages_router.post("/creation")
async def page_creation(
    current_user_id = Depends(get_current_user),
    page: int = Query(..., description="Придумайте номер новой страницы")
):
    async with engine.begin() as conn:

        update = await conn.execute(text(
            """
            INSERT INTO pages (user_id, page)
            VALUES (:user_id, :page)
            ON CONFLICT DO NOTHING
            """
        ), {"user_id": current_user_id, "page": page})

        if update.rowcount == 0:
            raise HTTPException(status_code=409, detail="Вы уже используете страницу с таким номером")
    
    return {"Страница": "добавлена"}

@pages_router.delete("/deletion")
async def page_deletion(
    page: int = Body(..., description="Введите номер страницы"),
    current_user_id = Depends(get_current_user)
):
    async with engine.begin() as conn:

        await conn.execute(text(
            """SELECT pg_advisory_xact_lock(:user_id)"""
        ), {"user_id": current_user_id})

        res = await conn.execute(text(
            """
            DELETE FROM pages
            WHERE page = :page AND user_id = :user_id
            """
        ), {"page": page, "user_id": current_user_id})

        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Страницы не сущетсвуте")
    
    return {"Страница": "Удалена"}

@pages_router.get("/{page}")
async def view_page(
    page: int               = Path(..., description="Номер страницы"),
    current_user_id: int    = Depends(get_current_user)
):
    async with engine.begin() as conn:
        res = await conn.execute(text(
            """
            SELECT nickname, weather, time, date, traffic, currencies 
            FROM pages
            WHERE page = :page AND user_id = :user_id
            """
        ), {"page": page, "user_id": current_user_id})

        page_widgets = {}
        res = res.mappings().first()

        if res is None:
            raise HTTPException(status_code=404, detail="Страница не найдена или пользователь не существует")

        if res["nickname"]:
            nickname = await conn.execute(text(
                """
                SELECT username FROM users
                WHERE id = :id
                """
            ), {"id": current_user_id})
            nickname = nickname.scalar_one_or_none()
            page_widgets["Имя пользователя"] = nickname
        
        todos = await conn.execute(text(
            """
            SELECT number, task FROM todos
            WHERE user_id = :user_id AND date = :today
            """
        ), {"user_id": current_user_id, "today": date.today()})

        todos = todos.mappings().all()
        if todos:
            page_widgets["Задачи"] = todos
        
        diet = await conn.execute(text(
            """
            SELECT breakfast, lunch, dinner FROM diets
            WHERE date = :today AND user_id = :user_id
            """
        ), {"user_id": current_user_id, "today": date.today()})

        diet = diet.mappings().first()
        if diet:
            page_widgets["Рацион"] = dict(diet)



    if res["weather"]:
        page_widgets["Погода"] = await get_weather()
        
    if res["time"]:
        page_widgets["Время"] = datetime.now().time()
        
    if res["date"]:
        page_widgets["Дата"] = datetime.now().date()
        
    if res["traffic"]:
        page_widgets["Пробки"] = str(random.randint(1, 10)) + " баллов"

    if res["currencies"]:
        page_widgets["Курсы валют"] = await get_currencies()
    
    return page_widgets



