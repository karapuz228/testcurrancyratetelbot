import telebot
import datetime
import time
from threading import Thread
import requests
import psycopg2


def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def delete_result():
    time.sleep(600)
    con = psycopg2.connect(
        database="test1",
        user="postgres",
        password="********",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    cur.execute('DELETE FROM DATA *')
    cur.close()
    con.commit()
    con.close()


url = 'https://api.exchangeratesapi.io/'

bot = telebot.TeleBot('YOUR TOKEN HERE')
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Show rates', 'Exchange', 'History')
# keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
# keyboard2.row('Home')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Welcome to ExchangeRateBot, how can i help you?', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def response(message):
    if message.text.lower() == 'show rates':
        list_message(message)
    elif message.text.lower() == 'exchange':
        exchange_message(message)
    elif message.text.lower() == 'history':
        history_message(message)
    # elif message.text.lower() == 'home':
    #     start_message(message)
    elif message.text.lower() == 'help':
        help_message(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, '/list or show rates shows all the rates based on USD.\n/exchange allows you to '
                                      'exchange currency values. Just follow the instructions.\n/history provides you'
                                      ' a list of changes to a currencies for last 7 days.', reply_markup=keyboard1)


@bot.message_handler(commands=['list'])
def list_message(message):
    con = psycopg2.connect(
        database="test1",
        user="postgres",
        password="********",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    cur.execute('SELECT result from data')
    row = cur.fetchone()
    if row is None:
        try:
            r = requests.get(f'{url}latest?base=USD').json()

            result = f'CAD: {round(r["rates"]["CAD"], 2)}\n' \
                     f'HKD: {round(r["rates"]["HKD"], 2)}\n' \
                     f'ISK: {round(r["rates"]["ISK"], 2)}\n' \
                     f'PHP: {round(r["rates"]["PHP"], 2)}\n' \
                     f'DKK: {round(r["rates"]["DKK"], 2)}\n' \
                     f'HUF: {round(r["rates"]["HUF"], 2)}\n' \
                     f'CZK: {round(r["rates"]["CZK"], 2)}\n' \
                     f'GBP: {round(r["rates"]["GBP"], 2)}\n' \
                     f'RON: {round(r["rates"]["RON"], 2)}\n' \
                     f'SEK: {round(r["rates"]["SEK"], 2)}\n' \
                     f'IDR: {round(r["rates"]["IDR"], 2)}\n' \
                     f'INR: {round(r["rates"]["INR"], 2)}\n' \
                     f'BRL: {round(r["rates"]["BRL"], 2)}\n' \
                     f'RUB: {round(r["rates"]["RUB"], 2)}\n' \
                     f'HRK: {round(r["rates"]["HRK"], 2)}\n' \
                     f'JPY: {round(r["rates"]["JPY"], 2)}\n' \
                     f'THB: {round(r["rates"]["THB"], 2)}\n' \
                     f'CHF: {round(r["rates"]["CHF"], 2)}\n' \
                     f'EUR: {round(r["rates"]["EUR"], 2)}\n' \
                     f'MYR: {round(r["rates"]["MYR"], 2)}\n' \
                     f'BGN: {round(r["rates"]["BGN"], 2)}\n' \
                     f'TRY: {round(r["rates"]["TRY"], 2)}\n' \
                     f'CNY: {round(r["rates"]["CNY"], 2)}\n' \
                     f'NOK: {round(r["rates"]["NOK"], 2)}\n' \
                     f'NZD: {round(r["rates"]["NZD"], 2)}\n' \
                     f'ZAR: {round(r["rates"]["ZAR"], 2)}\n' \
                     f'MXN: {round(r["rates"]["MXN"], 2)}\n' \
                     f'SGD: {round(r["rates"]["SGD"], 2)}\n' \
                     f'AUD: {round(r["rates"]["AUD"], 2)}\n' \
                     f'ILS: {round(r["rates"]["ILS"], 2)}\n' \
                     f'KRW: {round(r["rates"]["KRW"], 2)}\n' \
                     f'PLN: {round(r["rates"]["PLN"], 2)}'
            bot.send_message(message.chat.id, text=result, reply_markup=keyboard1)
            cur.execute('INSERT INTO data (result, date) VALUES (%s, %s)', (result, datetime.date.today()))
            cur.close()
            con.commit()
            con.close()
            th = Thread(target=delete_result)
            th.start()
        except KeyError:
            bot.send_message(message.chat.id, 'Server Error', reply_markup=keyboard1)
    else:
        cur.execute('SELECT result from data')
        rows = cur.fetchone()
        for row in rows:
            bot.send_message(message.chat.id, text=row, reply_markup=keyboard1)
        cur.close()
        con.commit()
        con.close()
        th = Thread(target=delete_result)
        th.start()


curs = ["CAD", "HKD", "USD", "ISK", "PHP", "DKK", "HUF", "CZK", "GBP", "RON", "SEK", "IDR", "INR", "BRL", "RUB",
        "HRK", "JPY", "THB", "CHF", "EUR", "MYR", "BGN", "TRY", "CNY", "NOK", "NZD", "ZAR", "MXN", "SGD", "AUD",
        "ILS", "KRW", "PLN"]
base = ''
amount = ''
multiply = ''


@bot.message_handler(content_types=['text'])
def exchange_message(message):
    bot.send_message(message.chat.id, f'Enter a currency to exchange (must be in 3 letters format (USD)).\n'
                                      f'Available currencies: {curs}.')
    bot.register_next_step_handler(message, get_base)


def get_base(message):
    global base
    base = message.text
    if base.upper() not in curs:
        bot.send_message(message.chat.id, f'Enter a valid currency in valid format!')
        exchange_message(message)
    else:
        bot.send_message(message.chat.id, f'Enter an amount of {base.upper()} you want to exchange.')
        bot.register_next_step_handler(message, get_amount)


def get_amount(message):
    global amount
    amount = message.text
    if is_digit(amount) is False:
        bot.send_message(message.chat.id, f'Amount must be a digit!')
        get_base(message)
    else:
        bot.send_message(message.chat.id, f'Enter a currency to exchange for (3 letters format).')
        bot.register_next_step_handler(message, get_multiply)


def get_multiply(message):
    global multiply
    multiply = message.text
    if multiply.upper() not in curs:
        bot.send_message(message.chat.id, f'Enter a valid currency in valid format! Try again.')
        exchange_message(message)
    else:
        try:
            r = requests.get(f'{url}latest?base={base.upper()}').json()
            res = float(amount) * float(r['rates'][multiply.upper()])
            bot.send_message(message.chat.id, f'{amount} {base.upper()} is {round(res, 2)} {multiply.upper()}.',
                             reply_markup=keyboard1)
        except KeyError:
            bot.send_message(message.chat.id, 'Server not responding.', reply_markup=keyboard1)


symbol1 = ''
symbol2 = ''
delta7 = datetime.timedelta(days=7)


@bot.message_handler(content_types=['text'])
def history_message(message):
    bot.send_message(message.chat.id, f'Enter first currency. Must be in 3 letters format (USD).\n'
                                      f'Available currencies: {curs}.')
    bot.register_next_step_handler(message, get_symbol1)


def get_symbol1(message):
    global symbol1
    symbol1 = message.text
    if symbol1.upper() not in curs:
        bot.send_message(message.chat.id, f'Enter a valid currency in valid format!')
        history_message(message)
    else:
        bot.send_message(message.chat.id, f'Enter second currency. Also in 3 letters format.')
        bot.register_next_step_handler(message, get_symbol2)


def get_symbol2(message):
    global symbol2
    symbol2 = message.text
    if symbol2.upper() not in curs:
        bot.send_message(message.chat.id, f'Enter a valid currency in valid format!')
        history_message(message)
    else:
        try:
            r = requests.get(
                f'{url}history?start_at={str(datetime.datetime.now()-delta7)[:10]}&end_at='
                f'{str(datetime.datetime.now())[:10]}&symbols={symbol1.upper()},{symbol2.upper()}').json()
            bot.send_message(message.chat.id, text=str(r['rates']), reply_markup=keyboard1)
        except KeyError:
            bot.send_message(message.chat.id, 'No exchange rate data is available for the selected currencies.',
                             reply_markup=keyboard1)


bot.polling(none_stop=True)
