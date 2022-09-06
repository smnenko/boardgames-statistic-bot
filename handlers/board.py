from gettext import gettext as _

from telebot import types

from constants import UserStatusChoice
from main import *
from models import *
from utils import IDsOptionUtil


@bot.callback_query_handler(func=lambda c: c.data == 'add_board')
async def add_board_handler(callback: types.CallbackQuery, ):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(_('Назад'), callback_data='main')
    )
    await bot.edit_message_text(
        _('1. Создайте чат в TG\n'
          '2. Пригласите туда всех игроков\n'
          '3. Добавьте бота и дайте ему права администратора\n'
          '4. Вызовите бота из чата командой /bot'),
        callback.message.chat.id,
        callback.message.message_id
    )


@bot.callback_query_handler(func=lambda c: c.data == 'delete')
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
            types.InlineKeyboardButton(_('Добавить результаты'), callback_data='userchoice'),
            types.InlineKeyboardButton(_('Подробная статистика'), callback_data='detailed_stat')
        )

        await bot.send_message(
            message.chat.id,
            _('Бот для ведения статистики настольних игр к вашим услугам!'),
            reply_markup=markup
        )
    else:
        await bot.send_message(
            message.chat.id,
            _('Данная команда предназначена только для групп')
        )


@bot.callback_query_handler(func=lambda c: c.data.startswith('userchoice'))
async def log_user_choice_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=2)
    profiles = [i.id for i in Profile.select().where(
        Profile.board == Board.select().where(Board.group_id == callback.message.chat.id))]

    if '_' in callback.data.removeprefix('userchoice_'):
        users_status = IDsOptionUtil.from_str(callback.data.removeprefix('userchoice_'), UserStatusChoice.values())
    else:
        users_status = IDsOptionUtil(ids=profiles, options=UserStatusChoice.values())

    markup.add(
        *[
            types.InlineKeyboardButton(
                f"{Profile.select().where(Profile.id == i).get().user.username} {'✅' if j == UserStatusChoice.PLAY.value else '❌'}",
                callback_data='userchoice_' + users_status.get_ids_option(i).to_str()
            )
            for i, j in users_status
        ]
    )
    markup.add(types.InlineKeyboardButton(_('Далее'), callback_data=f'usersave_{users_status.to_str()}'))
    markup.add(types.InlineKeyboardButton(_('Отмена'), callback_data='delete'))

    await bot.edit_message_text(
        _('Выберите игроков, которые принимали участие в игре'),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('usersave'))
async def log_user_save_handler(callback: types.CallbackQuery):
    users_status = IDsOptionUtil.from_str(callback.data.removeprefix('usersave_'))
    profile_ids = [f'{i}' for i, j in users_status if j == UserStatusChoice.PLAY.value]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        *[
            types.InlineKeyboardButton(i.name, callback_data=f"gamechoice_{i.id}_{','.join(profile_ids)}")
            for i in Game.select()
        ],
        types.InlineKeyboardButton(_('Отмена'), callback_data='delete')
    )

    await bot.edit_message_text(
        _('Выберите игру из списка:'),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('gamechoice'))
async def log_game_choice_handler(callback: types.CallbackQuery):
    if ',' in callback.data:
        game, profiles = callback.data.removeprefix('gamechoice_').split('_')
        profiles = Profile.select().where(Profile.id << profiles.split(',')).join(User)
        game = Game.select().where(Game.id == int(game)).get()

        game_results = []
        for i in profiles:
            game_results.append(GameResult.create(profile=i, game=game))

        markup = types.InlineKeyboardMarkup(row_width=1)
        game_roles = [i for i in game.roles]

        if '_' in callback.data.removeprefix('gamechoice_'):
            result_roles = IDsOptionUtil.from_str(callback.data.removeprefix('gamechoice_'), game_roles)
        else:
            result_roles = IDsOptionUtil(ids=[i.id for i in game_results], options=game_roles)

        if game_roles:
            markup.add(
                *[
                    types.InlineKeyboardButton(
                        f"{GameResult.select().where(GameResult.id == i).get().profile.user.username}"
                        f"[{GameRole.select().where(GameRole.id == j).get().name}]",
                        callback_data='gamechoice_' + result_roles.get_ids_option(i).to_str())
                    for i, j in result_roles
                ],
                types.InlineKeyboardButton('Далее',
                                           callback_data='setrole_' + callback.data.removeprefix('gamechoice_'))
            )

            await bot.edit_message_text(
                _(
                    f'Настолочка: {game.name}\n' +
                    f'Игроков: {len(profiles)}\n\n' +
                    f'Выберите роль для участников игры'
                ),
                callback.message.chat.id,
                callback.message.message_id,
                reply_markup=markup
            )
    else:
        await bot.edit_message_text(
            _(f'Настолочка: {game.name}\nИгроков: {len(profiles)}\n'),
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda c: c.data.startswith('setrole'))
async def set_result_profile_role(callback: types.CallbackQuery):
    profile, role = callback.data.removeprefix('setrole_').split('_')
    profile = Profile.select().where(Profile.id == profile)
    role = GameRole.select().where(GameRole.id == role)
