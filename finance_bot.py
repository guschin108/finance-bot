#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import json
import sys
from excur.excur import *
from telegram import *
from telegram.ext import *

logging.basicConfig(format='Finance bot: %(levelname)s: %(name)s: %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

main_kb = [['Обмен валют']]

def bot_start(update, context):
    kb = main_kb
    user = update.message.from_user.first_name
    update.message.reply_text(
        'Привет, ' + user + '!\n'
        '\nЯ простой финансовый бот 💰\n'
        '\nСписок команд:'
        '\n*Обмен валют* - Показать лучший курс обмена валют',
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True),
        parse_mode=ParseMode.MARKDOWN)


CITY, CURRENCY = range(2)

cities_ru_en = {
    'Астрахань' : 'Astrakhan',
    'Барнаул' : 'Barnaul',
    'Владивосток' : 'Vladivostok',
    'Волгоград' : 'Volgograd',
    'Воронеж' : 'Voronezh',
    'Екатеринбург' : 'Yekaterinburg',
    'Ижевск' : 'Izhevsk',
    'Иркутск' : 'Irkutsk',
    'Казань' : 'Kazan',
    'Кемерово' : 'Kemerovo',
    'Краснодар' : 'Krasnodar',
    'Красноярск' : 'Krasnoyarsk',
    'Махачкала' : 'Makhachkala',
    'Москва' : 'Moscow',
    'Набережные Челны' : 'Naberezhnye_Chelny',
    'Нижний Новгород' : 'Nizhniy_Novgorod',
    'Новокузнецк' : 'Novokuzneck',
    'Новосибирск' : 'Novosibirsk',
    'Омск' : 'Omsk',
    'Оренбург' : 'Orenburg',
    'Пенза' : 'Penza',
    'Пермь' : 'Perm',
    'Ростов-на-Дону' : 'Rostov-On-Don',
    'Рязань' : 'Ryazan',
    'Самара' : 'Samara',
    'Санкт-Петербург' : 'Saint-Petersburg',
    'Саратов' : 'Saratov',
    'Тольятти' : 'Tolyatti',
    'Томск' : 'Tomsk',
    'Тюмень' : 'Tyumen',
    'Ульяновск' : 'Ulyanovsk',
    'Уфа' : 'Ufa',
    'Хабаровск' : 'Khabarovsk',
    'Челябинск' : 'Chelyabinsk',
    'Ярославль' : 'Yaroslavl',
}

cities_ru = list(cities_ru_en.keys())

city_fkb = [[x] for x in list(cities_ru)]
city_fkb.append(['Отмена'])

city_kb = [['Новосибирск'], ['Москва'], ['Другие города'], ['Отмена']]

currencies = ['Доллар США', 'Евро']
currency_kb = [currencies, ['Отмена']]

def exchange_rate_start(update, context):
    user = update.message.from_user.first_name
    kb = city_kb
    update.message.reply_text(
        'Обмен валют: выберите город!',
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

    return CITY

def exchange_rate_other_city(update, context):
    user = update.message.from_user.first_name
    kb = city_fkb
    update.message.reply_text(
        'Обмен валют: выберите город!',
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

    return CITY

def exchange_rate_city(update, context):
    city = update.message.text
    context.user_data['city'] = city

    kb = currency_kb
    update.message.reply_text(
        'Обмен валют: выберите валюту!',
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

    return CURRENCY

def exchange_rate_make_answer(context):
    try:
        city = cities_ru_en[context.user_data['city']]
    except:
        raise

    try:
        currency = context.user_data['currency']
    except:
        raise

    try:
        data = excur_get_data(city)
    except:
        raise

    if currency == 'Доллар США':
        return ('Продать Доллар США : *' + excur_usd_best_buy_get(data) + '*\n'
                'Купить Доллар США  : *' + excur_usd_best_sell_get(data) + '*\n'
                '\nИнформация получена с сайта '
                '[excur.ru](https://excur.ru/' + city + ')')
    elif currency == 'Евро':
        return ('Продать Евро : *' + excur_euro_best_buy_get(data) + '*\n'
                'Купить Евро  : *' + excur_euro_best_sell_get(data) + '*\n'
                '\nИнформация получена с сайта '
                '[excur.ru](https://excur.ru/' + city + ')')
    raise

def exchange_rate_done(context):
    if 'city' in context.user_data:
        del context.user_data['city']

    if 'currency' in context.user_data:
        del context.user_data['currency']

def exchange_rate_currency(update, context):
    currency = update.message.text
    context.user_data['currency'] = currency

    answer = ''

    try:
        answer = exchange_rate_make_answer(context)
    except:
        answer = 'Запрос не выполнен, попробуйте позже!'

    kb = main_kb
    update.message.reply_text(
        answer,
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True)

    exchange_rate_done(context)
    return ConversationHandler.END

def exchange_rate_cancel(update, context):
    kb = main_kb
    update.message.reply_text(
        'Отменено',
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

    exchange_rate_done(context)
    return ConversationHandler.END

def main(token):
    updater = Updater(token, use_context=True)

    exchange_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Обмен валют'),
                      exchange_rate_start)],
        states={
            CITY: [MessageHandler(Filters.text(cities_ru),
                                  exchange_rate_city),
                   MessageHandler(Filters.text('Другие города'),
                                  exchange_rate_other_city)],
            CURRENCY: [MessageHandler(Filters.text(currencies),
                       exchange_rate_currency)],
        },
        fallbacks=[MessageHandler(Filters.text, exchange_rate_cancel)]
    )

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', bot_start))
    dp.add_handler(exchange_handler)

    updater.start_polling(poll_interval=1, timeout=5, bootstrap_retries=3)

    logger.info('Ready!')
    updater.idle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Finance bot")
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args()

    try:
        config = json.load(open(args.config, 'r'))
    except:
        logger.error('configuration file not found or formatted incorrectly')
        exit()

    try:
        token = config['token']
    except:
        logger.error('token not specified')
        exit()

    main(token)
