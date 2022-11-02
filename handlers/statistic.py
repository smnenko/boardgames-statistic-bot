import inject
from peewee import fn
from telebot import TeleBot, types

from constants import GameResultStatus, ProfileResultStatusChoice, PREV_BUTTON
from models import *


bot = inject.instance(TeleBot)


@bot.callback_query_handler(func=lambda c: c.data == 'statistic')
def statistic_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    results = GameResult.select().where(GameResult.board == board, GameResult.status == GameResultStatus.FINISHED.value)
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='main')
    )
    text = f'Общее количество игр: {results.count()}\n\n'
    for i in board.profiles:
        wins = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.WIN.value).count()
        draws = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DRAW.value).count()
        defeats = results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DEFEAT.value).count()
        total = wins + draws + defeats
        text += (
            f'@{i.user.username} <unranked>\n'
            f'    Побед — {wins}\n'
            f'    Ничьих — {draws}\n'
            f'    Поражений — {defeats}\n'
            f'    Вин рейт — {wins / total * 100 if total != 0 else 0}%\n\n'
        )
    # text += 'Мини-достижения:\n'
    # subquery = (
    #     ProfileResult
    #         .select(ProfileResult.profile, fn.COUNT(ProfileResult.status))
    #         .join(GameResult)
    #         .where(
    #         GameResult.board == board,
    #         GameResult.status == GameResultStatus.FINISHED.value,
    #         ProfileResult.status == ProfileResultStatusChoice.WIN.value
    #     )
    #         .group_by(ProfileResult.profile)
    # )
    # query = subquery.select(ProfileResult.profile, fn.MAX(ProfileResult.status)).get()
    # text += f"    @{query.profile.user.username} — больше всего побед {query.max}\n"
    # for i in board.games:
    #     if i.is_score:
    #         max_score = ProfileResult.select(fn.MAX(ProfileResult.score)).join(GameResult).where(
    #             GameResult.game == i).scalar()
    #         profile_result = ProfileResult.select().join(GameResult).where(GameResult.game == i,
    #                                                                        ProfileResult.score == max_score).get()
    #         text += f"    @{profile_result.profile.user.username} — лучший счёт {max_score} в игре {i.name}\n"
    bot.edit_message_text(
        text,
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
