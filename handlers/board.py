import os
from itertools import cycle

import inject
from telebot import TeleBot, types

from constants import *
from models import *
from utils import get_game_info, get_game_settings_markup

bot = inject.instance(TeleBot)


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
    bot.delete_message(message.chat.id, message.message_id)
    if message.chat.id < 0:
        board, created = Board.get_or_create(group_id=message.chat.id)
        for i in (i for i in bot.get_chat_administrators(message.chat.id) if not i.user.is_bot):
            user, created = User.get_or_create(chat_id=i.user.id, username=i.user.username)
            Profile.get_or_create(user=user.id, board=board.id)

        markup = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton('Добавить результат', callback_data='add_result'),
            types.InlineKeyboardButton('Статистика', callback_data='statistic'),
            types.InlineKeyboardButton('Настройки', callback_data='settings'),
            types.InlineKeyboardButton(HIDE_BUTTON, callback_data='hide')
        )

        bot.send_message(
            message.chat.id,
            'Бот для ведения статистики настольних игр к вашим услугам!',
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
        'Бот для ведения статистики настольних игр к вашим услугам!',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'add_result')
def add_result_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    games = Game.select().where(Game.is_visible == True, Game.is_active == True, Game.board == board).order_by(Game.id.desc())
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[types.InlineKeyboardButton(i.name, callback_data=f'add_profiles_{i.id}') for i in games],
    ).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='main'),
        row_width=1
    )
    bot.edit_message_text(
        'Выберите игру:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_profiles'))
def add_profiles_handler(callback: types.CallbackQuery):
    game = Game.select().where(Game.id == callback.data.removeprefix('add_profiles_')).get()
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    profiles = Profile.select().where(Profile.board == board).order_by(Profile.id.desc())
    result, is_created = GameResult.get_or_create(game=game, board=board, status=GameResultStatus.STARTED.value)

    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(f'❌ {i.user.username}', callback_data=f'add_profile_{i.id}_{result.id}')
            for i in profiles
        ]
    ).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='add_result'),
        row_width=1
    )
    bot.edit_message_text(
        f'Игра: {game.name}\n'
        f'Роли: {"Включены" if [i for i in game.roles] else "Выключены"}\n'
        f'Счёт: {"Включен" if game.is_score else "Выключен"}\n'
        f'\nВыберите игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_profile'))
def add_profile_handler(callback: types.CallbackQuery):
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
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'add_profiles_{result.game.id}'),
        row_width=1
    )

    bot.edit_message_text(
        f'Игра: {result.game.name}\n'
        f'Роли: {"Включены" if [i for i in result.game.roles] else "Выключены"}\n'
        f'Счёт: {"Включен" if result.game.is_score else "Выключен"}\n'
        f'\nВыберите игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data.startswith('add_roles'))
def add_roles_handler(callback: types.CallbackQuery):
    if callback.data.endswith('change'):
        result_id, profile_result_id = callback.data.removeprefix('add_roles_').removesuffix('_change').split('_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_result = ProfileResult.select().where(ProfileResult.id == profile_result_id).get()

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

    profile_results = ProfileResult.select().where(ProfileResult.game_result == result).order_by(
        ProfileResult.id.desc())
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
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'add_profiles_{result.game.id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
        row_width=1
    )
    bot.edit_message_text(
        'Выберите роли для игроков:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_scores'))
def add_scores_handler(callback: types.CallbackQuery):
    if callback.data.endswith('_change'):
        result_id, profile_result_id, score = callback.data.removeprefix('add_scores_').removesuffix('_change').split(
            '_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_result = ProfileResult.select().where(ProfileResult.id == profile_result_id).get()

        if int(score) == 0:
            profile_result.score = 0
        else:
            profile_result.score += int(score)
        profile_result.save()

        profile_result = ProfileResult.select().where(ProfileResult.id == profile_result_id).get()
        markup = types.InlineKeyboardMarkup(row_width=5).add(
            types.InlineKeyboardButton('-10', callback_data=f'add_scores_{result_id}_{profile_result_id}_-10_change'),
            types.InlineKeyboardButton('-1', callback_data=f'add_scores_{result_id}_{profile_result_id}_-10_change'),
            types.InlineKeyboardButton('0', callback_data=f'add_scores_{result_id}_{profile_result_id}_0_change'),
            types.InlineKeyboardButton('+1', callback_data=f'add_scores_{result_id}_{profile_result_id}_1_change'),
            types.InlineKeyboardButton('+10', callback_data=f'add_scores_{result_id}_{profile_result_id}_10_change'),
            types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_scores_{result_id}'),
            types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'add_profiles_{result.game.id}'),
            types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete')
        )
        bot.edit_message_text(
            f'{profile_result.profile.user.username} — {profile_result.score}',
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup
        )
    else:
        result_id = callback.data.removeprefix('add_scores_')
        result = GameResult.select().where(GameResult.id == result_id).get()
        profile_results = ProfileResult.select().where(ProfileResult.game_result == result)

        for i in profile_results:
            if i.score == None:
                i.score = 0
                i.save()

        profile_results = ProfileResult.select().where(ProfileResult.game_result == result)
        markup = types.InlineKeyboardMarkup(row_width=5).add(
            *[
                types.InlineKeyboardButton(
                    f'[{i.score}] {i.profile.user.username}',
                    callback_data=f'add_scores_{result_id}_{i.id}_0_change'
                ) for i in profile_results
            ]
        ).add(
            types.InlineKeyboardButton(NEXT_BUTTON, callback_data=f'add_statuses_{result_id}'),
            types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'add_profiles_{result.game.id}'),
            types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
            row_width=1
        )
        bot.edit_message_text(
            'Выберите:',
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda c: c.data.startswith('add_statuses'))
def add_statuses_handler(callback: types.CallbackQuery):
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

    profile_results = ProfileResult.select().where(ProfileResult.game_result == result).order_by(
        ProfileResult.id.desc())
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
        types.InlineKeyboardButton('💠 Завершить', callback_data=f'finish_game_{result_id}'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'add_profiles_{result.game.id}'),
        types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='delete'),
        row_width=1
    )
    bot.edit_message_text(
        'Выберите исход для каждого игрока:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('finish_game'))
def finish_game_handler(callback: types.CallbackQuery):
    result_id = callback.data.removeprefix('finish_game_')
    result = GameResult.select().where(GameResult.id == result_id).get()
    result.status = GameResultStatus.FINISHED.value
    result.save()
    bot.answer_callback_query(callback.id, 'Игра успешно записана в статистику', show_alert=False)
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)


@bot.callback_query_handler(func=lambda c: c.data == 'settings')
def settings_handler(callback: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(callback.message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Игры', callback_data='settings_game'),
        types.InlineKeyboardButton('Пожелания и предложения', callback_data='suggestions'),
        types.InlineKeyboardButton('Поддержать автора', url=os.environ.get('DONATE_AUTHOR')),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='main')
    )
    bot.edit_message_text(
        'Выберите:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'settings_game')
def settings_game_handler(callback: types.CallbackQuery):
    board = Board.select().where(Board.group_id == callback.message.chat.id).get()
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(f'{i.name}', callback_data=f'edit_game_{i.id}')
            for i in Game.select().where(Game.board == board).order_by(Game.id.desc())
        ]
    ).add(
        types.InlineKeyboardButton('Добавить игру', callback_data='new_game'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='settings'),
        row_width=1
    )
    bot.edit_message_text(
        'Список игр:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_game'))
def edit_game_handler(callback: types.CallbackQuery):
    if '_score' in callback.data or '_visible' in callback.data or '_delete' in callback.data:
        game_id = callback.data.removeprefix('edit_game_').removesuffix('_score').removesuffix('_visible').removesuffix('_delete')
        game = Game.select().where(Game.id == game_id).get()
        if '_score' in callback.data:
            game.is_score = not game.is_score
        if '_visible' in callback.data:
            game.is_visible = not game.is_visible
        game.save()

        if '_delete' in callback.data:
            Game.delete().where(Game.id == game_id).execute()
            bot.answer_callback_query(callback.id, 'Игра удалена')

        bot.edit_message_text(
            get_game_info(game),
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=get_game_settings_markup(game)
        )
    else:
        game_id = callback.data.removeprefix('edit_game_')
        game = Game.select().where(Game.id == game_id).get()
        bot.edit_message_text(
            get_game_info(game),
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=get_game_settings_markup(game)
        )


@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_roles_'))
def edit_roles_handler(callback: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(callback.message.chat.id)
    game_id = callback.data.removeprefix('edit_roles_')
    game = Game.select().where(Game.id == game_id).get()
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[
            types.InlineKeyboardButton(i.name, callback_data=f'edit_role_{i.id}')
            for i in game.roles
        ]
    ).add(
        types.InlineKeyboardButton('Добавить роль', callback_data=f'append_role_{game_id}'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'edit_game_{game_id}'),
        row_width=1
    )
    bot.edit_message_text(
        'Выберите:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_role_'))
def edit_role_handler(callback: types.CallbackQuery):
    role_id = callback.data.removeprefix('edit_role_')
    role = GameRole.select().where(GameRole.id == role_id).get()
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Удалить', callback_data=f'delete_role_{role_id}'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'edit_roles_{role.game.id}'),
    )
    bot.edit_message_text(
        f'ID: {role_id}\n'
        f'Название: {role.name}\n'
        f'Родитель: {role.parent.name if role.parent else "-"}\n\n'
        f'Дата создания: {role.created_at.strftime("%d %B, %Y")}',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('delete_role'))
def append_role_handler(callback: types.CallbackQuery):
    role_id = callback.data.removeprefix('delete_role_')
    role = GameRole.select().where(GameRole.id == role_id).get()
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('➡️ К настройкам', callback_data=f'edit_game_{role.game.id}')
    )
    GameRole.delete().where(GameRole.id == role_id).execute()
    bot.edit_message_text(
        'Роль удалена',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('append_role'))
def append_role_handler(callback: types.CallbackQuery):
    game_id = callback.data.removeprefix('append_role_')
    game = Game.select().where(Game.id == game_id).get()

    def append_role_name_handler(message: types.Message):
        role = GameRole.create(game=game, name=message.text)
        bot.delete_message(message.chat.id, message.message_id)
        markup = types.InlineKeyboardMarkup(row_width=1).add(
            *[
                types.InlineKeyboardButton(i.name, callback_data=f'set_parent_role_{role.id}_{i.id}')
                for i in game.roles if i.id != role.id
            ],
            types.InlineKeyboardButton('➡️ Без родителя', callback_data=f'edit_game_{game_id}')
        )
        bot.edit_message_text(
            f'Выберите родителя для роли {role.name}',
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup
        )

    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'edit_roles_{game_id}')
    )
    msg = bot.edit_message_text(
        f'Введите название новой роли для игры с названием: {game.name}',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, append_role_name_handler)


@bot.callback_query_handler(func=lambda c: c.data.startswith('set_parent_role'))
def set_parent_role_handler(callback: types.CallbackQuery):
    role_id, parent_id = callback.data.removeprefix('set_parent_role_').split('_')
    role = GameRole.select().where(GameRole.id == role_id).get()
    parent = GameRole.select().where(GameRole.id == parent_id).get()
    role.parent = parent
    role.save()
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data=f'edit_game_{role.game.id}')
    )
    bot.edit_message_text(
        'Роль успешно обновлена',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'new_game')
def new_game_handler(callback: types.CallbackQuery):

    def create_game_handler(message: types.Message):
        board = Board.select().where(Board.group_id == message.chat.id).get()
        game = Game.create(name=message.text, board=board, is_visible=True, is_active=True)
        bot.delete_message(message.chat.id, message.message_id)
        markup = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton('➡️ К настройкам', callback_data=f'edit_game_{game.id}')
        )
        bot.edit_message_text(
            f'Игра с названием {message.text} успешно создана',
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup
        )

    msg = bot.edit_message_text(
        'Введите название новой настольной игры:',
        callback.message.chat.id,
        callback.message.message_id
    )
    bot.register_next_step_handler(msg, create_game_handler)


def send_suggestions_handler(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='settings')
    )
    bot.send_message(os.environ.get('SUGGESTIONS_GROUP_ID'), message.text)
    bot.delete_message(message.chat.id, message.message_id)
    bot.edit_message_text(
        'Ваше пожелание успешно доставлено',
        message.chat.id,
        message.message_id - 1,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'suggestions')
def suggestions_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='settings')
    )
    msg = bot.edit_message_text(
        'Напишите пожелания или предложение по боту и я обязательно доставлю ваше письмо разработчику\n\n'
        'Учтите, что чем детальнее вы опишите ваше пожелание или проблему с которой вы столкнулись, '
        'тем точнее получится воплотить вашу идею в жизнь',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, send_suggestions_handler)
