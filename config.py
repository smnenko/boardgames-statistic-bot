import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from peewee import PostgresqlDatabase
from telebot.async_telebot import AsyncTeleBot


def configuration(binder):
    logger = logging.getLogger('board_games_statistic')
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('BOT | %(asctime)s | %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    load_dotenv()

    app = FastAPI()
    db = PostgresqlDatabase(
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )
    bot = AsyncTeleBot(token=os.environ.get('BOT_TOKEN'))

    binder.bind(logging.Logger, logger)
    binder.bind(FastAPI, app)
    binder.bind(PostgresqlDatabase, db)
    binder.bind(AsyncTeleBot, bot)

    asyncio.run(bot.remove_webhook())
    asyncio.run(bot.set_webhook(f"{os.environ.get('WEBHOOK_HOST')}/{os.environ.get('WEBHOOK_URL')}"))
