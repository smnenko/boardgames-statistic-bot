from telebot import types

from constants import *
from main import *
from models import *
from utils import IDsOptionUtil


@bot.callback_query_handler(func=lambda c: c.data == 'add_board')
async def add_board_handler(callback: types.CallbackQuery, ):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data='main')
    )
    await bot.edit_message_text(
        '1. Создайте чат в TG\n'
        '2. Пригласите туда всех игроков\n'
        '3. Добавьте бота и дайте ему права администратора\n'
        '4. Вызовите бота из чата командой /bot',
        callback.message.chat.id,
        callback.message.message_id
    )


@bot.callback_query_handler(func=lambda c: c.data == 'delete')
async def delete_message(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id)
    GameResult.select().where(GameResult.board == board, GameResult.status == GameResultStatus.STARTED.value).get().delete_instance()
    await bot.delete_message(
        callback.message.chat.id,
        callback.message.message_id
    )


@bot.callback_query_handler(func=lambda c: c.data == 'hide')
async def delete_message(callback: types.CallbackQuery):
    await bot.delete_message(
        callback.message.chat.id,
        callback.message.message_id
    )


@bot.message_handler(commands=['bot'])
async def call_bot(message: types.Message):
    if message.chat.id < 0:
        board, created = Board.get_or_create(group_id=message.chat.id)
        for i in (await bot.get_chat_administrators(message.chat.id)):
            user, created = User.get_or_create(chat_id=i.user.id, username=i.user.username)
            Profile.get_or_create(user=user.id, board=board.id)

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton('Добавить результаты', callback_data='add_result'),
            types.InlineKeyboardButton('Подробная статистика', callback_data='detailed_stat'),
            types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='hide')
        )

        await bot.send_message(
            message.chat.id,
            'Бот для ведения статистики настольних игр к вашим услугам!',
            reply_markup=markup
        )
    else:
        await bot.send_message(
            message.chat.id,
            'Данная команда предназначена только для групп'
        )


@bot.callback_query_handler(func=lambda c: c.data == 'add_result')
async def game_choice_handler(callback: types.CallbackQuery):
    games = Game.select().where(Game.is_visible == True, Game.is_active == True)
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        *[types.InlineKeyboardButton(i.name, callback_data=f'add_profiles_{i.id}') for i in games],
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='hide')
    )
    await bot.edit_message_text(
        'Выберите игру:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_profiles'))
async def profiles_choice_handler(callback: types.CallbackQuery):
    game = Game.select().where(Game.id == callback.data.removeprefix('add_profiles_')).get()
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    profiles = Profile.select().where(Profile.board == board)
    result = GameResult.get_or_create(game=game, board=board)

    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(f'❌ {i.user.username}', callback_data=f'add_profile_{i.id}_{result.id}')
            for i in profiles
        ],
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete')
    )
    await bot.edit_message_text(
        f'Игра: {game.name}\n'
        f'Роли: {"Включены" if [i for i in game.roles] else "Выключены"}\n'
        f'Счёт: {"Включен" if game.is_score else "Выключен"}\n'
        f'\nВыберите игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_profile'))
async def profile_choice_handler(callback: types.CallbackQuery):
    profile_id, result_id = callback.data.removeprefix('add_profile_').split('_')
    profile = Profile.select().where(Profile.id == profile_id).get()
    result = GameResult.select().where(GameResult.id == result_id).get()
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()

    profile_result_ids = [
        i.profile.id for i in ProfileResult.select(ProfileResult.profile).where(ProfileResult.game_result == result)
    ]
    if profile.id not in profile_result_ids:
        ProfileResult.create(game_result=result, profile=profile)
    else:
        ProfileResult.delete().where(
            ProfileResult.game_result == result, ProfileResult.profile == profile
        ).execute()
    profile_result_ids = [
        i.profile.id for i in ProfileResult.select(ProfileResult.profile).where(ProfileResult.game_result == result)
    ]

    profiles = Profile.select().where(Profile.board == board)
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(
                f'✅ {i.user.username}' if i.id in profile_result_ids else f'❌ {i.user.username}',
                callback_data=f'add_profile_{i.id}_{result.id}')
            for i in profiles
        ],
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_roles_{result_id}')
        if [i for i in result.game.roles] else
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_score_{result_id}')
        if result.game.is_score else
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_win_{result_id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete')
    )

    await bot.edit_message_text(
        f'Игра: {result.game.name}\n'
        f'Роли: {"Включены" if [i for i in result.game.roles] else "Выключены"}\n'
        f'Счёт: {"Включен" if result.game.is_score else "Выключен"}\n'
        f'\nВыберите игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('setrole'))
async def set_result_profile_role(callback: types.CallbackQuery):
    pass
