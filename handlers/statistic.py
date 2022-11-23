from decimal import Decimal

import inject
from telebot import TeleBot, types

from constants import GameResultStatus, ProfileResultStatusChoice, PREV_BUTTON
from models import *
from utils.statistic import StatisticUtil

bot = inject.instance(TeleBot)


@bot.callback_query_handler(func=lambda c: c.data == 'statistic')
def statistic_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    results = GameResult.select().where(GameResult.board == board, GameResult.status == GameResultStatus.FINISHED.value)
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(f'@{i.user.username}', callback_data=f'statistic_{i.id}')
            for i in board.profiles
        ]
    ).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='main'), row_width=1
    )
    text = f'Общее количество игр: {results.count()}\n\n'
    for i in board.profiles:
        wins = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.WIN.value).count()
        draws = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DRAW.value).count()
        defeats = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DEFEAT.value).count()
        total = wins + draws + defeats
        wr = round(Decimal(wins / total * 100), 1) if total != 0 else 0
        profile_points = ProfileRank.select().where(ProfileRank.profile == i).get().points
        profile_rank = Rank.get_by_points(profile_points).name
        text += f'{profile_rank} @{i.user.username} — {wr}%\n'

    bot.edit_message_text(
        text,
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('statistic'))
def statistic_profile_handler(callback: types.CallbackQuery):
    profile_id = callback.data.removeprefix('statistic_')
    profile = Profile.select().where(Profile.id == profile_id).get()
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Статистика по играм', callback_data=f'game_statistic_{profile_id}'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='statistic')
    )
    wins = ProfileResult.select().where(ProfileResult.profile == profile, ProfileResult.status == ProfileResultStatusChoice.WIN.value).count()
    draws = ProfileResult.select().where(ProfileResult.profile == profile, ProfileResult.status == ProfileResultStatusChoice.DRAW.value).count()
    defeats = ProfileResult.select().where(ProfileResult.profile == profile, ProfileResult.status == ProfileResultStatusChoice.DEFEAT.value).count()
    total = wins + draws + defeats
    wr = round(Decimal(wins / total * 100), 1) if total != 0 else 0
    profile_points = ProfileRank.select().where(ProfileRank.profile == profile).get().points
    profile_rank = Rank.get_by_points(profile_points).name
    bot.edit_message_text(
        f'{profile_rank} @{profile.user.username} — {wr}%\n'
        f'        Сыграно — {profile.results.count()}\n'
        f'        Побед — {wins}\n'
        f'        Ничьих — {draws}\n'
        f'        Поражений — {defeats}\n'
        f'        Рейтинг — {profile_points}',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup,
        parse_mode='markdown'
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('game_statistic'))
def statistic_profile_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    games = Game.select().where(
        Game.board == board,
        Game.is_visible == True,
        Game.is_active == True
    ).order_by(Game.created_at.asc())
    if callback.data.endswith('_change'):
        profile_id, game_id = callback.data.removeprefix('game_statistic_').removesuffix('_change').split('_')
        profile = Profile.select().where(Profile.id == profile_id).get()
        game = games.where(Game.id == game_id).get()
    else:
        profile_id = callback.data.removeprefix('game_statistic_')
        profile = Profile.select().where(Profile.id == profile_id).get()
        game = games.limit(1).get()
    games = games.where(Game.id != game.id)

    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(i.name, callback_data=f'game_statistic_{profile_id}_{i.id}_change')
            for i in games
        ]
    ).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'statistic_{profile_id}'), row_width=1
    )
    bot.edit_message_text(
        StatisticUtil.game(profile, game),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
