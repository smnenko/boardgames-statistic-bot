import asyncio
import os
from logging import Logger

import inject
import uvicorn
from fastapi import FastAPI, Request, Response
from peewee import PostgresqlDatabase
from telebot import types
from telebot import TeleBot

import config


inject.configure_once(config.configuration)
from handlers import *

logger = inject.instance(Logger)
app = inject.instance(FastAPI)
db = inject.instance(PostgresqlDatabase)
bot = inject.instance(TeleBot)


@app.post(f"/{os.environ.get('WEBHOOK_URL')}")
async def telegram_updates_handler(request: Request):
    if request.headers.get('content-type') == 'application/json':
        update = types.Update.de_json(await request.json())
        bot.process_new_updates([update])
        await asyncio.sleep(1)
        return Response(status_code=200)
    return Response(status_code=403)


if __name__ == '__main__':
    logger.info('Started')

    db.connect()

    uvicorn.run('main:app', use_colors=True, reload=True)

