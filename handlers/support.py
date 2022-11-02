import inject
from telebot import TeleBot, types

from constants import PREV_BUTTON

bot = inject.instance(TeleBot)


@bot.callback_query_handler(func=lambda c: c.data == 'support')
def support_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('Как добавить статистику?', callback_data='support_how_track_statistic'),
        types.InlineKeyboardButton('Как добавить игру?', callback_data='support_how_create_game'),
        types.InlineKeyboardButton('Как добавить роли к игре?', callback_data='support_how_add_roles'),
        types.InlineKeyboardButton('Как считать очки?', callback_data='support_count_points'),
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='settings')
    )
    bot.edit_message_text(
        'Выберите необходимый для вас вопрос:',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'support_how_track_statistic')
def support_how_track_statistic_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='support')
    )
    bot.edit_message_text(
        'Для того, чтобы вести статистику по играм необходимо создать игру и правильно её настроить, '
        'вам останется только пройти все этапы в меню "Добавить результат"',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'support_how_create_game')
def support_how_create_game_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='support')
    )
    bot.edit_message_text(
        'Для того, чтобы создать игру необходимо пройти в меню Настройки -> Игры -> Добавить игру и выбрать название '
        'для игры. Бот рекомендует писать осмысленные и правильные названия для игр, ибо так будет сложнее запутаться '
        'в своих записях.',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'support_how_add_roles')
def support_count_points_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='support')
    )
    bot.edit_message_text(
        'Роли — ещё одна немаловажная механика, которую автор со всей душой вложил в мои алгоритмы. Проследуйте в меню '
        'Настройки -> [Название вашей игры] -> Управление ролями -> Добавить роль\n\n'
        'Выберите название для роли. Возьмём в пример игру "Мафия", напишите по запросу бота слово "Мирный", '
        'затем по точно такому же алгоритму добавьте роль "Мафия". Когда бот попросит указать родителя, выберите пункт '
        '"Без родителя", но когда вы захотите добавить роль "Шериф", выберите в качестве родителя роль "Мирный", '
        'потому что Шериф — это мирный игрок.',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data == 'support_count_points')
def support_count_points_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(PREV_BUTTON, callback_data='support')
    )
    bot.edit_message_text(
        'Очки — не менее важная деталь, чем роли. Очки важно учитывать в таких играх, как Каркассон и, к примеру, '
        'Ticket To Ride (Билет на поезд). Чтобы включить в игре функцию подсчёта очков, необходимо перйти в меню '
        'Настройки -> Игры -> [Название вашей игры] и нажать на кнопку "Включить счёт"',
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=markup
    )
