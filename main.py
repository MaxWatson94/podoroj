from telebot import types
from config import TOKEN
import pandas as pd
import requests
import telebot
import sqlite3
import time


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):

    # ОСНОВНОЕ МЕНЮ
    mainMenu = types.ReplyKeyboardMarkup(row_width=2)
    checkBalance = types.KeyboardButton('Баланс')
    addCart = types.KeyboardButton('Добавить карту')
    pay = types.KeyboardButton('Пополнить баланс')
    mainMenu.add(checkBalance, addCart, pay)
    bot.send_message(message.chat.id, "Привет " + message.from_user.username + '!\n\nЯ - бот который поможет следить за балансом на карте "Подорожник". Добавьте свою карту и начните следить за своим балансом.\n\nПо вопросам и предложениям @MaxWatson', reply_markup=mainMenu)

    conn = sqlite3.connect('db/users.db')
    cur = conn.cursor()
    userID = message.from_user.id
    userName = message.from_user.username
    try:
        cur.execute("""INSERT INTO users(userid, username, carNumber, lastBalance) 
                VALUES (?,?,?,?);""", (userID, userName, 0, 0))
        conn.commit()
        print("Добавлен новый пользователь!")
    except:
        print("Пользователь уже существует")




@bot.message_handler(func=lambda message: message.text == "Добавить карту")
def addCart(message):
    msg = bot.send_message(message.chat.id, 'Введите номер карты')
    bot.register_next_step_handler(msg, askCart)

def askCart(message):
    # Определаяем переменные с сообщением польщвоателя с его номером карты и его ЙД
    carNumber = message.text
    userID = message.from_user.id
    try:
        # Открываем базу данных
        sqlite_connection = sqlite3.connect('db/users.db')
        cursor = sqlite_connection.cursor()
        # Записываем новую карту польщоватлю
        cursor.execute ("""UPDATE users SET carNumber = ? WHERE userid = ?""", (carNumber, userID))
        # Коммит в базе
        sqlite_connection.commit()
        # Закрываем соедение с базой
        cursor.close()
        # Пишем в консоль о новом добавление карты
        print("Пользователь добавил даные карты")
        # Заносим ЙД польщователя в переменную
        userID = message.from_user.id
        # Подключаемся к базе польщвоателей
        conn = sqlite3.connect('db/users.db')
        cur = conn.cursor()
        # Забираем установленный номер карты пользователя и выносим в переменную
        cur.execute("""SELECT carNumber FROM users WHERE userid = ?""", (userID,))
        userCard = cur.fetchone()
        cur.close()
        # Отправляем запрос
        r = requests.get('https://new.ltkarta.ru/fideth?&bsk=' + str(userCard))
        # Полученные данные в ввиде HTML заносим в переменную
        htmltext = r.text

        # Ищем баланас между двуся словами более и руб
        word1 = 'более'
        word2 = 'руб'
        balance = htmltext[htmltext.find(word1)+5 : htmltext.find(word2)]


        # ОСНОВНОЕ МЕНЮ
        mainMenu = types.ReplyKeyboardMarkup(row_width=2)
        checkBalance = types.KeyboardButton('Баланс')
        addCart = types.KeyboardButton('Добавить карту')
        pay = types.KeyboardButton('Пополнить баланс')
        mainMenu.add(checkBalance, addCart, pay)

        # Проверка на содержание ошибок
        if "error" in balance:
            bot.send_message(message.chat.id, "Ошибка, проверьте данные карты и попробуйте снова\nНажмите 'Добавить карту'", reply_markup=mainMenu)            
        else:
            # Открываем базу данных
            sqlite_connection = sqlite3.connect('db/users.db')
            cursor = sqlite_connection.cursor()
            # Записываем последний баланс пользоватля
            cursor.execute ("""UPDATE users SET lastBalance = ? WHERE userid = ?""", (int(balance), userID))
            # Коммит в базе
            sqlite_connection.commit()
            # Закрываем соедение с базой
            cursor.close()
            # Отправляем баланс
            bot.send_message(message.chat.id, "Карта добавлена ✅\n\nБаланас на карте: " + balance + '₽', reply_markup=mainMenu)

    except:
        # Отправляем сообщение пользователю в чат в случаии ошибки
        bot.send_message(message.chat.id, 'Что-то пошло не так, проверьте данные и попробуйте снова. Введите команду /add')






@bot.message_handler(func=lambda message: message.text == "Баланс")
def balance(message):
    # Записываем ЙД польщователя
    userID = message.from_user.id

    # Соеденяемся с БД
    conn = sqlite3.connect('db/users.db')
    cur = conn.cursor()

    # Получаем нмоер карты из БД
    cur.execute("""SELECT carNumber FROM users WHERE userid = ?""", (userID,))
    userCard = cur.fetchone()
    cur.close()

    # Првоеряем на наличие карты
    if userCard == "0":
        bot.send_message(message.chat.id, "Вы не добавили карту!\nДобавьте карту или измените текущую.")
    # Если карта есть то
    else:
        # Кидаем запрос
        r = requests.get('https://new.ltkarta.ru/fideth?&bsk=' + str(userCard))
        # Полученные данные в ввиде HTML записываем в переменную
        htmltext = r.text

        # Ищем баланас между двуся словами более и руб
        word1 = 'более'
        word2 = 'руб'
        balance = htmltext[htmltext.find(word1)+5 : htmltext.find(word2)]

        if "error" in balance:
            bot.send_message(message.chat.id, "Ошибка, проверьте данные карты")            
        else:
            # Открываем базу данных
            sqlite_connection = sqlite3.connect('db/users.db')
            cursor = sqlite_connection.cursor()
            # Записываем последний баланс пользоватля
            cursor.execute ("""UPDATE users SET lastBalance = ? WHERE userid = ?""", (int(balance), userID))
            # Коммит в базе
            sqlite_connection.commit()
            # Закрываем соедение с базой
            cursor.close()
            # Отправляем баланс
            ridesSubWay = int(balance) / 45
            ridesBus = int(balance) / 40
            balacnceInfo = "\n\nХватит на " + str(round(ridesSubWay)) + " поездок на метро и на " + str(round(ridesBus)) + ' поездок на наземном траспорте.' + '\n\nПриятных поездок!'
            bot.send_message(message.chat.id, "Ваш баланас: " + balance + ' ₽' + str(balacnceInfo))


@bot.message_handler(func=lambda message: message.text == "Пополнить баланс")
def balance(message):
    msg = bot.send_message(message.chat.id, 'Введите сумму для оплаты\nМаксимальная сумма пополнения 14 581₽')
    bot.register_next_step_handler(msg, pay)


def pay(message):
    # Записываем ЙД польщователя в перменную
    userID = message.from_user.id
    # Получаем номер карты из БД
    conn = sqlite3.connect('db/users.db')
    cur = conn.cursor()
    cur.execute("""SELECT carNumber FROM users WHERE userid = ?""", (userID,))
    userCard = cur.fetchone()
    cur.close()

    # Проверяем наличие карты
    if userCard == '0' or 0:
        bot.send_message(message.chat.id, 'Вы не добавили карту!')
    else:
        # Получаем FID для оплаты Его можно получить из запроса по типу BSK
        r = requests.get('https://new.ltkarta.ru/fideth?&bsk=' + str(userCard))
        # Полученные данные в ввиде HTML записываем в переменную
        htmltext = r.text
        # Ищем FID между двумя словами 
        word1 = 'fid'
        word2 = "clear'"
        fid = htmltext[htmltext.find(word1)+14 : htmltext.find(word2)-93]
        # Делаем запрос на оплтау
        r2 = requests.get('https://new.ltkarta.ru/fideth?&user_lang=ru&type=1??amount=' + str(message.text) + '?bsk=' + str(userCard) + '?fid=' + str(fid))

        redirectTioPay = r2.text

        # Ищем FID между двумя словами 
        word3 = 'https:'
        word4 = '"}'
        payLink = redirectTioPay[redirectTioPay.find(word3) : redirectTioPay.find(word4)]

        formatLinlk = payLink.replace('\/', '/')

        PayButton = types.InlineKeyboardMarkup()
        link = types.InlineKeyboardButton(text='Оплатить', url=formatLinlk)
        PayButton.add(link)
        
        bot.send_message(message.chat.id, 'Проверьте данные:\n\nСумма пополнения: ' + str(message.text) + '₽\nНомер карты: ' + str(userCard[0]) + '\n\nВы будете перенаправлены на страницу оплаты.', reply_markup = PayButton)


@bot.message_handler(commands=["send"])
def answer(message):
    conn = sqlite3.connect('db/users.db')
    cur = conn.cursor()
    cur.execute("SELECT userid FROM users")
    allusers = cur.fetchall()
    for i in range(len(allusers)):
        time.sleep(1)
        bot.send_message(int(allusers[i]['id']), "13123" )
        print(allusers[i])




bot.infinity_polling()