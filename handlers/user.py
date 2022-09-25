from gettext import gettext as _

import inject
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from models import User


bot = inject.instance(AsyncTeleBot)


@bot.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    User.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(_('Добавить стол'), callback_data='add_board'),
        types.InlineKeyboardButton(_('Профиль'), callback_data='profile'),
        types.InlineKeyboardButton(_('Помощь'), callback_data='help')
    )
    await bot.send_message(
        message.chat.id,
        _('Это бот для контроля статистики по настолочкам!'),
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'main')
async def main_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(_('Добавить стол'), callback_data='add_board'),
        types.InlineKeyboardButton(_('Профиль'), callback_data='profile'),
        types.InlineKeyboardButton(_('Помощь'), callback_data='help')
    )
    await bot.edit_message_text(
        _('Это бот для контроля статистики по настолочкам!'),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'profile')
async def profile_handler(callback: types.CallbackQuery):
    user = User.select().where(User.chat_id == callback.message.chat.id).get()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(_('Назад'), callback_data='main')
    )
    await bot.edit_message_text(
        f"ID: {user.chat_id}\nusername: {user.username}",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
