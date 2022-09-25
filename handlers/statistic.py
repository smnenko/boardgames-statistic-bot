import inject
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from constants import GameResultStatus, ProfileResultStatusChoice, CANCEL_BUTTON
from models import *


bot = inject.instance(AsyncTeleBot)


@bot.callback_query_handler(func=lambda c: c.data == 'statistic')
async def statistic_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    results = GameResult.select().where(GameResult.board == board, GameResult.status == GameResultStatus.FINISHED.value)
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.InlineKeyboardButton(i.user.username, callback_data=f'statistic_detailed_{i.id}')
            for i in board.profiles
        ],
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='hide')
    )
    await bot.edit_message_text(
        f'Сыграно игр: {results.count()}\n\n' +
        '\n'.join(
            f'{i.user.username}'.ljust(10, ' ') + ' '
            f'{str(results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.WIN.value).count() + results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DRAW.value).count()).center(3, " ")}' +
            f'{str(results.join(ProfileResult).where(ProfileResult.profile == i, ProfileResult.status == ProfileResultStatusChoice.DEFEAT.value).count()).center(3, " ")}'
            for i in board.profiles
        ) +
        '\n\nВыберите игрока для просмотра детальной статистики:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('statistic_detailed'))
async def statistic_detailed_handler(callback: types.CallbackQuery):
    profile = Profile.select().where(Profile.id == callback.data.removeprefix('statistic_detailed_')).get()
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('⬅️ Назад', callback_data='statistic')
    )
