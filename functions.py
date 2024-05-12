import telebot
from telebot import types
import pandas as pd
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def showRefSystem(message, user_id):
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_table')
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == user_id:
            ref_quality = row[2]
            referral_link = row[4]
            bot.send_message(message.chat.id, f'Рефералы: {ref_quality}\n'
                                              f'Ваша реферальная ссылка: <code>{referral_link}</code>', parse_mode = 'HTML')

def generate_referral_link(message):
    referral_link = f"https://t.me/CcCalendar_bot?start=ref={message.from_user.id}"
    return referral_link

bot = telebot.TeleBot("6462832900:AAFLxUqTH7frm9CpCAMU2SZWAbHkxn5jsTo")

def userInfoReveal(message):
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_table')
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == message.from_user.id:
            markup = types.InlineKeyboardMarkup(row_width = 1)
            btn1 = types.InlineKeyboardButton('Реферальная система', callback_data='ref_system')
            markup.add(btn1)
            username = row[3]
            wallet = row[6]
            bot.send_message(message.chat.id, f'{username}\n'
                                              f'Ваш кошелек: {wallet}\n', reply_markup=markup)

def userCase(message):
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_table WHERE id_user = ?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is not None:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Реферальная система', callback_data='ref_system')
        markup.add(btn1)
        username = row[3]
        wallet = row[6]
        bot.send_message(message.chat.id, f'Вы уже участвуете в розыгрыше\n'
                                          f'{username}\n'
                                          f'Ваш кошелек: {wallet}\n', reply_markup=markup)
    else:
        subscribeToChannels(message)

def checkUserExistanceDB(message):
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_table')
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == message.from_user.id:
            return True
        else:
            return False

def getChannelsLinks():
    file = open('channels_links.txt', 'r')
    list_channel = file.readlines()
    file.close()
    list_channel = [list_channel_edited.strip() for list_channel_edited in list_channel]
    return list_channel

def subscribeToChannels(message):
    links_list = getChannelsLinks()
    markup = types.InlineKeyboardMarkup(row_width=1)
    number = 1
    for link in links_list:
        btn = createButtonURL(link, number)
        markup.add(btn)
        number += 1
    btn = createButtonCheck()
    markup.add(btn)
    bot.send_message(message.chat.id, 'Подпишитесь на все нужные каналы\n!Примечание: Если вы подписаны и кнопка "проверить не работает" - переподпишитесь', reply_markup=markup)

def adminPanel(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Обновить группы', callback_data='update_groups')
    btn2 = types.InlineKeyboardButton('Обновить google таблицу', callback_data='update_sheet')
    btn3 = types.InlineKeyboardButton("Изменить стартовое сообщение", callback_data='change_start_message')
    markup.add(btn1,btn2, btn3)
    bot.send_message(message.chat.id, 'Панель администратора', reply_markup=markup)

def adminCase(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton('Админ панель', callback_data="admin_panel")
    markup.add(btn)
    bot.send_message(message.chat.id, 'Доброго времени суток, админ', reply_markup=markup)

def checkAdmin(message):
    admin_list = [663349082, 9171055234]
    result = False
    for admin in admin_list:
        if admin == message.from_user.id:
            result = True
            break
        else:
            pass
    return result

def tableCreation():
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    cursor = db.cursor()
    user_table = """ CREATE TABLE IF NOT EXISTS user_table (id INTEGER PRIMARY KEY, id_user INTEGER, ref_quality INTEGER, username TEXT, referral_link TEXT, referrer_id INTEGER, wallet TEXT)"""
    cursor.execute(user_table)
    db.commit()

def checkUsername(username):
    if username.startswith("@"):
        return True
    else:
        return False

def saveUser(message, username, wallet, referrer_id = None):
    referral_link = generate_referral_link(message)
    db = sqlite3.connect('db/database.db', check_same_thread=False)
    id_user = message.from_user.id
    cursor = db.cursor()
    if referrer_id is not None:
        cursor.execute(f"INSERT INTO user_table (id_user, ref_quality, username, referral_link, referrer_id, wallet) VALUES ('{id_user}', '0', '{username}', '{referral_link}', '{referrer_id}', '{wallet}')")
    else:
        cursor.execute(f"INSERT INTO user_table (id_user, ref_quality, username, referral_link, wallet) VALUES ('{id_user}', '0', '{username}', '{referral_link}', '{wallet}')")
    db.commit()
    if referrer_id is not None:
        cursor.execute("UPDATE user_table SET ref_quality = ref_quality + 1 WHERE id_user = ?", (referrer_id,))
    db.commit()

def getChannelsList():
    file = open('channels_web.txt', 'r')
    list_channel = file.readlines()
    file.close()
    list_channel = [list_channel_edited.strip() for list_channel_edited in list_channel]
    return list_channel

def getChannelIDList():
    channel_list = getChannelsList()
    channel_id_list = []
    for link in channel_list:
        parts = link.split('-')
        if len(parts) > 1:
            channel_id = parts[-1]
            new_channel_id = '-100' + channel_id
            channel_id_list.append(new_channel_id)
    return channel_id_list


def checkSubscribtion(id_user):
    channel_id_list = getChannelIDList()
    is_subscribed = True

    for channel_id in channel_id_list:
        try:
            chat_member = bot.get_chat_member(channel_id, id_user)
            print(chat_member)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                is_subscribed = False
                break
        except Exception as e:
            print(f"Error for channel {channel_id}: {e}")
            is_subscribed = False
            break

    return is_subscribed

def createButtonURL(channel, number):
    btn = types.InlineKeyboardButton(f"Канал {number}", url=f'{channel}')
    return btn

def createButtonCheck():
    btn = types.InlineKeyboardButton('Проверить подписки', callback_data='check_sub')
    return btn

def fileWriteChannelsInfo(message, file_name):
    if ',' in message.text:
        channels = message.text.split(',')

        channels = [word.strip() for word in channels]

        with open(f'{file_name}.txt', 'w') as file:
            file.write('\n'.join(channels))

        bot.send_message(message.chat.id, "Данные успешно сохранены.")
    else:
        channels = message.text
        with open(f'{file_name}.txt', 'w') as file:
            file.write(channels)

        bot.send_message(message.chat.id, "Данные успешно сохранены.")


def dataToGoogleSheet():
    try:
        db_path = 'db/database.db'
        conn = sqlite3.connect(db_path)
        query = 'SELECT * FROM user_table'
        df = pd.read_sql(query, con=conn)
        df = df.astype(str)

        headers = ['id', 'id пользователя', 'рефералы', 'Имя пользователя', 'Реферальная ссылка', 'id того, что пригласил', 'кошелек']

        credentials_file = 'creds.json'
        spreadsheet_id = '1L5za4iWVjjrjJJK_EU5R-yYQazVnv_wo7GbCIowmcVY'

        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])
        client = gspread.authorize(credentials)

        sheet = client.open_by_key(spreadsheet_id).sheet1
        sheet.clear()
        data = [headers] + df.values.tolist()
        sheet.insert_rows(data)
        return True
    except Exception as e:
        print(e)
        return False