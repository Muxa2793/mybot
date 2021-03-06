import datetime
import ephem
import logging
import os

from db import (db, get_or_create_user, subscribe_user, unsubscribe_user, save_meme_image_vote,
                user_voted, get_image_rating)
from glob import glob
from random import choice
from utils import play_random_numbers, main_keyboard, is_cat, meme_rating_inline_keyboard
from jobs import alarm


def greet_user(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    logging.info('Вызван /start')
    update.message.reply_text(f'Привет, пользователь! Ты вызвал команду /start.\n'
                              f'/planet <название_планеты> - узнать в каком созвездии находится планета;\n'
                              f'Доступные планеты: Марс, Венера, Юпитер.\n'
                              f'/next_full_moon - узнать когда ближайшее полнолуние;\n'
                              f'/guess <число> - поиграть с ботом в числа;\n'
                              f'/meme - увидеть мемасик по Python {user["emoji"]};',
                              reply_markup=main_keyboard())


def guess_number(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    logging.info('Вызван /guess')
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except (TypeError, ValueError):
            message = 'Введите целое число'
    else:
        message = 'Введите число'
    update.message.reply_text(message, reply_markup=main_keyboard())


def send_python_meme(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    logging.info('Запрошен мемасик')
    python_meme = glob('images/python*.jp*g')
    random_meme = choice(python_meme)
    chat_id = update.effective_chat.id
    if user_voted(db, random_meme, user['user_id']):
        rating = get_image_rating(db, random_meme)
        keyboard = None
        caption = f'Рейтинг мемасика: {rating}'
    else:
        keyboard = meme_rating_inline_keyboard(random_meme)
        caption = None
    context.bot.send_photo(
        chat_id=chat_id,
        photo=open(random_meme, 'rb'),
        reply_markup=keyboard,
        caption=caption
        )


def user_coordinates(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    logging.info("Запрошены координаты")
    coords = update.message.location
    update.message.reply_text(
        f"Ваши координаты {coords} {user['emoji']}!", reply_markup=main_keyboard()
    )


def planet(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    print(context.args)
    logging.info(context.args)
    if context.args[0].lower() == 'марс':
        logging.info('вызвана команда /planet Марс')
        now = datetime.datetime.now()
        mars = ephem.Mars(now)
        stars = ephem.constellation(mars)
        star_planet = (f'Сегодняшняя дата {now.strftime("%d-%m-%Y %H:%M")}.\n'
                       f'Планета Марс находится в созвездии {stars[1]}')
        update.message.reply_text(star_planet, reply_markup=main_keyboard())
    elif context.args[0].lower() == 'юпитер':
        logging.info('вызвана команда /planet Юпитер')
        now = datetime.datetime.now()
        jupiter = ephem.Jupiter(now)
        stars = ephem.constellation(jupiter)
        star_planet = (f'Сегодняшняя дата {now.strftime("%d-%m-%Y %H:%M")}.\n'
                       f'Планета Юпитер находится в созвездии {stars[1]}')
        update.message.reply_text(star_planet, reply_markup=main_keyboard())
    elif context.args[0].lower() == 'венера':
        logging.info('вызвана команда /planet Венера')
        now = datetime.datetime.now()
        venus = ephem.Venus(now)
        stars = ephem.constellation(venus)
        star_planet = (f'Сегодняшняя дата {now.strftime("%d-%m-%Y %H:%M")}.\n'
                       f'Планета Венера находится в созвездии {stars[1]}')
        update.message.reply_text(star_planet, reply_markup=main_keyboard())
    else:
        logging.info('вызвана команда неизвестная планета')
        update.message.reply_text('Такой планеты нет в моём списке!',
                                  reply_markup=main_keyboard())


def next_full_moon(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    logging.info('вызвана команда /next_full_moon')
    now = datetime.datetime.now()
    full_moon = ephem.next_full_moon(now)
    update.message.reply_text(f'Ближайшее полнолуние произойдёт: {full_moon}', reply_markup=main_keyboard())


def check_user_photo(update, context):
    get_or_create_user(db, update.effective_user, update.message.chat.id)
    update.message.reply_text('Обрабатываем фотографию')
    os.makedirs('downloads', exist_ok=True)
    user_photo = context.bot.getFile(update.message.photo[-1].file_id)
    file_name = os.path.join('downloads', f'{user_photo.file_id}.jpg')
    user_photo.download(file_name)
    if is_cat(file_name):
        update.message.reply_text('Обнаружен мемасик, добавляю в библиотеку')
        new_filename = os.path.join('images', f'meme_{user_photo.file_id}.jpg')
        os.rename(file_name, new_filename)
    else:
        update.message.reply_text('МЕМАС НЕ ОБНАРУЖЕН!!')
        os.remove(file_name)


def subscribed(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    subscribe_user(db, user)
    update.message.reply_text('Вы успешно подписались')


def unsubscribed(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    unsubscribe_user(db, user)
    update.message.reply_text('Вы отписались')


def set_alarm(update, context):
    try:
        alarm_seconds = abs(int(context.args[0]))
        context.job_queue.run_once(alarm, alarm_seconds, context=update.message.chat.id)
        update.message.reply_text(f'Уведомление через {alarm_seconds} секунд')
    except (ValueError, TypeError):
        update.message.reply_text('Введите целое число секунд после команды')


def meme_picture_raiting(update, context):
    update.callback_query.answer()
    callback_type, image_name, vote = update.callback_query.data.split('|')
    vote = int(vote)
    user = get_or_create_user(db, update.effective_user, update.effective_chat.id)
    save_meme_image_vote(db, user, image_name, vote)
    rating = get_image_rating(db, image_name)
    update.callback_query.edit_message_caption(caption=f'Рейтин мемасика: {rating}')
