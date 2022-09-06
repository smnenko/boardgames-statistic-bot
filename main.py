import asyncio
import os
import logging

from dotenv import load_dotenv
from peewee import PostgresqlDatabase
from fastapi import FastAPI
from telebot.async_telebot import AsyncTeleBot

from models import *


logger = logging.getLogger('board_games_statistic')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('BOT | %(asctime)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
logger.addHandler(sh)


load_dotenv()

app = FastAPI()
db = PostgresqlDatabase(
    database=os.environ.get('DB_NAME', ),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)
bot = AsyncTeleBot(token=os.environ.get('BOT_TOKEN'))


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

    from handlers import *
    asyncio.run(bot.polling(skip_pending=True, timeout=60))

    # uvicorn.run('main:app', use_colors=True)

