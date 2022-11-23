import inject
from telebot import TeleBot, types

from constants import GameResultStatus, HIDE_BUTTON
from models import *


bot = inject.instance(TeleBot)


@bot.my_chat_member_handler()
def my_chat_member_handler(message: types.ChatMemberUpdated):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Скрыть это сообщение', callback_data='hide')
    )
    new = message.new_chat_member
    if new.status == 'member':
        bot.send_message(
            message.chat.id,
            'Всем привет, я бот, который будет вести статистику по настольным играм за вашим столом. Для того, чтобы '
            'вызвать меня и как-то со мной взаимодействовать используйте команду /bot\n\n'
            'Ответы на практически все вопросы вы можете найти в меню Настройки -> Помощь\n\n'
            'Не забудьте дать боту и всем участникам данного чата права администратора, чтобы бот мог присылать и '
            'удалять свои сообщения, а так же отслеживать участников вашего чата.\n\n'
            'Так же вам стоит знать, что разработал меня тот ещё придирчивый настольщик, поэтому бот будет максимально '
            'незаметен в вашем ламповом чатике и все сообщения от бота можно будет скрыть при помощи кнопки, похожей '
            'на эту:',
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda c: c.data == 'delete')
def delete_message(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id)
    GameResult.select().where(GameResult.board == board,
                              GameResult.status == GameResultStatus.STARTED.value).get().delete_instance()
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda c: c.data == 'hide')
def hide_message(callback: types.CallbackQuery):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.message_handler(commands=['bot'])
def bot_command_handler(message: types.Message):
    if message.chat.id < 0:
        board, created = Board.get_or_create(group_id=message.chat.id)
        for i in (i for i in bot.get_chat_administrators(message.chat.id) if not i.user.is_bot):
            user, created = User.get_or_create(chat_id=i.user.id)
            if user.username != i.user.username:
                user.username = i.user.username
                user.save()
            profile, _ = Profile.get_or_create(user=user.id, board=board)
            profile_rank, created = ProfileRank.get_or_create(profile=profile)
            if created:
                profile_rank.points = 0
                profile_rank.save()

        markup = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton('Добавить результат', callback_data='add_result'),
            types.InlineKeyboardButton('Статистика', callback_data='statistic'),
            types.InlineKeyboardButton('Настройки', callback_data='settings'),
            types.InlineKeyboardButton(HIDE_BUTTON, callback_data='hide')
        )
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(
            message.chat.id,
            'Бот для ведения статистики настольных игр к вашим услугам!',
            reply_markup=markup,
            disable_notification=True
        )
    else:
        bot.send_message(
            message.chat.id,
            'Данная команда предназначена только для групп'
        )


@bot.callback_query_handler(func=lambda c: c.data == 'main')
def main_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Добавить результат', callback_data='add_result'),
        types.InlineKeyboardButton('Статистика', callback_data='statistic'),
        types.InlineKeyboardButton('Настройки', callback_data='settings'),
        types.InlineKeyboardButton(HIDE_BUTTON, callback_data='hide')
    )

    bot.edit_message_text(
        'Бот для ведения статистики настольных игр к вашим услугам!',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
