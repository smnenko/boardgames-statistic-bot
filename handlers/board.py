from itertools import cycle

import inject
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from constants import *
from models import *


bot = inject.instance(AsyncTeleBot)


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
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)


@bot.callback_query_handler(func=lambda c: c.data == 'hide')
async def delete_message(callback: types.CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)


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
            types.InlineKeyboardButton('Статистика', callback_data='statistic'),
            types.InlineKeyboardButton('Информация', callback_data='information'),
            types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='hide')
        )

        await bot.send_message(
            message.chat.id,
            'Бот для ведения статистики настольних игр к вашим услугам!',
            reply_markup=markup,
            disable_notification=True
        )
    else:
        await bot.send_message(
            message.chat.id,
            'Данная команда предназначена только для групп'
        )


@bot.callback_query_handler(func=lambda c: c.data == 'add_result')
async def add_result_handler(callback: types.CallbackQuery):
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
async def add_profiles_handler(callback: types.CallbackQuery):
    game = Game.select().where(Game.id == callback.data.removeprefix('add_profiles_')).get()
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    profiles = Profile.select().where(Profile.board == board).order_by(Profile.id.desc())
    result, is_created = GameResult.get_or_create(game=game, board=board, status=GameResultStatus.STARTED.value)

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
async def add_profile_handler(callback: types.CallbackQuery):
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

    profiles = Profile.select().where(Profile.board == board).order_by(Profile.id.desc())
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(
                f'✅ {i.user.username}' if i.id in profile_result_ids else f'❌ {i.user.username}',
                callback_data=f'add_profile_{i.id}_{result.id}')
            for i in profiles
        ],
    ).add(
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_roles_{result_id}')
        if [i for i in result.game.roles] else
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_scores_{result_id}')
        if result.game.is_score else
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_statuses_{result_id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
        row_width=1
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


@bot.callback_query_handler(lambda c: c.data.startswith('add_roles'))
async def add_roles_handler(callback: types.CallbackQuery):
    if callback.data.endswith('change'):
        result_id, profile_result_id = callback.data.removeprefix('add_roles_').removesuffix('_change').split('_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_result = ProfileResult.select().where(ProfileResult.id == profile_result_id).get()
        profile_results = ProfileResult.select().where(ProfileResult.game_result == result)

        roles = [i for i in result.game.roles]
        roles_cycle = cycle(roles)
        next_role = next(roles_cycle)
        while True:
            this_role, next_role = next_role, next(roles_cycle)
            if this_role == profile_result.role:
                profile_result.role = next_role
                profile_result.save()
                break

    else:
        result_id = callback.data.removeprefix('add_roles_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_results = ProfileResult.select().where(ProfileResult.game_result == result)

        for i in profile_results:
            if i.role == None:
                i.role = result.game.roles.first()
                i.save()

    profile_results = ProfileResult.select().where(ProfileResult.game_result == result).order_by(ProfileResult.id.desc())
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(
                f'[{i.role.name if i.role else "-"}] {i.profile.user.username}',
                callback_data=f'add_roles_{result_id}_{i.id}_change'
            ) for i in profile_results
        ]
    ).add(
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_scores_{result_id}')
        if result.game.is_score else
        types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_statuses_{result_id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
        row_width=1
    )
    await bot.edit_message_text(
        'Выберите роли для игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_scores'))
async def add_scores_handler(callback: types.CallbackQuery):
    pass


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_statuses'))
async def add_wins_handler(callback: types.CallbackQuery):
    if callback.data.endswith('change'):
        result_id, profile_result_id = callback.data.removeprefix('add_statuses_').removesuffix('_change').split('_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_result = ProfileResult.select().where(ProfileResult.id == profile_result_id).get()

        statuses = ProfileResultStatusChoice.values()
        statuses_cycle = cycle(statuses)
        next_status = next(statuses_cycle)
        while True:
            this_status, next_status = next_status, next(statuses_cycle)
            if this_status == profile_result.status:
                profile_result.status = next_status
                profile_result.save()
                break

    else:
        result_id = callback.data.removeprefix('add_statuses_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_results = ProfileResult.select().where(ProfileResult.game_result == result)

        for i in profile_results:
            if i.status == None:
                i.status = ProfileResultStatusChoice.DEFEAT.value
                i.save()

    profile_results = ProfileResult.select().where(ProfileResult.game_result == result).order_by(ProfileResult.id.desc())
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        *[
            types.InlineKeyboardButton(
                f"{'❌ ' if i.status == ProfileResultStatusChoice.DEFEAT.value else ''}"
                f"{'⚠️ ' if i.status == ProfileResultStatusChoice.DRAW.value else ''}"
                f"{'✅ ' if i.status == ProfileResultStatusChoice.WIN.value else ''} "
                f"{i.profile.user.username}",
                callback_data=f'add_statuses_{result_id}_{i.id}_change'
            )
            for i in profile_results
        ]
    ).add(
        types.InlineKeyboardButton('Завершить', callback_data=f'finish_game_{result_id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
        row_width=1
    )
    await bot.edit_message_text(
        'Выберите исход для каждого игрока:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('finish_game'))
async def finish_game_handler(callback: types.CallbackQuery):
    result_id = callback.data.removeprefix('finish_game_')
    result = GameResult.select().where(GameResult.id == result_id).get()
    result.status = GameResultStatus.FINISHED.value
    result.save()
    await bot.answer_callback_query(callback.id, 'Игра успешно записана в статистику', show_alert=False)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
