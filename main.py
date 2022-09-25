import asyncio
import os
from logging import Logger

import inject
import uvicorn
from fastapi import FastAPI, Request, Response
from peewee import PostgresqlDatabase
from telebot import types
from telebot.async_telebot import AsyncTeleBot

import config


inject.configure_once(config.configuration)
from models import *
from handlers import *


logger = inject.instance(Logger)
app = inject.instance(FastAPI)
db = inject.instance(PostgresqlDatabase)
bot = inject.instance(AsyncTeleBot)


@app.post(f"/{os.environ.get('WEBHOOK_URL')}")
async def telegram_updates_handler(request: Request):
    if request.headers.get('content-type') == 'application/json':
        update = types.Update.de_json(await request.json())
        await bot.process_new_updates([update])
        return Response(status_code=200)
    return Response(status_code=403)


if __name__ == '__main__':
    logger.info('Started')

    db.connect()

    models = [Game, User, Profile, Board, GameRole, GameResult, ProfileResult]
    db.drop_tables(models)
    db.create_tables(models)

    game = Game.create(name='Мафия', slug='mafia', is_visible=True, is_score=False)
    mafia = GameRole.create(game=game, name='Мафия')
    peace = GameRole.create(game=game, name='Мирный')
    sheriff = GameRole.create(game=game, name='Шериф', parent=peace)
    uvicorn.run('main:app', use_colors=True, reload=True)

