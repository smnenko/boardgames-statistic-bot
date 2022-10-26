from telebot import types

from constants import PREV_BUTTON
from models import Game, GameRole


def get_game_info(game: Game):
    is_roles = True if [i for i in game.roles] else False
    if is_roles:
        is_roles = '\n  - ' + '\n  - ️'.join(i.name for i in game.roles)

    return (
        f'ID: {game.id}\n'
        f'Название: {game.name}\n'
        f'Роли: {is_roles if is_roles else "✖️"}\n'
        f'Счёт: {"✔️" if game.is_score else "✖️"}\n'
        f'Доступность: {"✔️" if game.is_visible else "✖️"}\n\n'
        f'Дата создания: {game.created_at.strftime("%d %B, %Y")}'
    )


def get_game_settings_markup(game: Game):
    return types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton(
                'Отключить счёт' if game.is_score else 'Включить счёт',
                callback_data=f'edit_game_{game.id}_score'
            ),
            types.InlineKeyboardButton(
                'Скрыть игру' if game.is_visible else 'Активировать игру',
                callback_data=f'edit_game_{game.id}_visible'
            ),
            types.InlineKeyboardButton(
                'Управление ролями',
                callback_data=f'edit_roles_{game.id}'
            ),
            types.InlineKeyboardButton('Удалить игру', callback_data=f'edit_game_{game.id}_delete'),
            types.InlineKeyboardButton(PREV_BUTTON, callback_data='settings_game')
        )