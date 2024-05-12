import telebot
from functions import checkSubscribtion
from functions import saveUser
from functions import tableCreation
from functions import checkUsername
from functions import dataToGoogleSheet
from functions import checkAdmin
from functions import adminCase
from functions import adminPanel
from functions import userCase
from functions import subscribeToChannels
from functions import userInfoReveal
from functions import fileWriteChannelsInfo
from functions import checkUserExistanceDB
from functions import showRefSystem

bot = telebot.TeleBot("6462832900:AAFLxUqTH7frm9CpCAMU2SZWAbHkxn5jsTo")
referrer_id = None

API_URL = f'https://api.telegram.org/bot6462832900:AAFLxUqTH7frm9CpCAMU2SZWAbHkxn5jsTo/'

@bot.message_handler(commands=["start"])
def start(message):
    global referrer_id
    global user_id
    user_id = message.from_user.id
    if checkAdmin(message):
        adminCase(message)
    else:
        tableCreation()
        file = open('start_message.txt', 'r', encoding='utf-8')
        bot.send_message(message.chat.id, file.read())
        file.close()
        if message.text.startswith("/start ref="):
            referrer_id = message.text.split('=')[1]
            userCase(message)
        else:
            userCase(message)

@bot.message_handler(content_types=["text"])

def anyMessageFromUser(message):
    bot.send_message(message.chat.id, 'Извините, я вас не понимаю. Для использования моего функционала, напишите "<code>/start</code>"', parse_mode='HTML')

def getUser(message):
    global referrer_id
    global username
    wallet = message.text
    if checkUserExistanceDB(message) == True:
        userInfoReveal(message)
    else:
        saveUser(message, username, wallet, referrer_id)
        userInfoReveal(message)

def sendMeWallet(message):
    global username
    username = message.text
    if checkUsername(username):
        bot.send_message(message.chat.id, 'Напишите мне ваш кошелек')
        bot.register_next_step_handler(message, getUser)
    else:
        bot.send_message(message.chat.id, 'Такого username не существует. Напишите username еще раз c "@"')
        bot.register_next_step_handler(message, sendMeWallet)


def sendMeUsername(message):
    bot.send_message(message.chat.id, 'Напишите мне ваш username с  "@"')
    bot.register_next_step_handler(message, sendMeWallet)

def sendMeGroups(message):
    bot.send_message(message.chat.id, 'Напишите мне ссылки на каналы, которые вы хотите добавить, через запятые\n!Все старые каналы будут удалены!')
    bot.register_next_step_handler(message, newChannels)

def newChannels(message):
    file_name = 'channels_web'
    fileWriteChannelsInfo(message, file_name)

    bot.send_message(message.chat.id,
                     'Напишите мне пригласительные ссылки каналов через запятые\n!Все старые пригласительные ссылки будут удалены!')
    bot.register_next_step_handler(message, newInviteLinks)

def newInviteLinks(message):
    file_name = 'channels_links'
    fileWriteChannelsInfo(message, file_name)
    bot.register_next_step_handler(message, sendMeGroups)

def sendMeStartMessage(message):
    bot.send_message(message.chat.id, 'Напишите мне все, что угодно. Абсолютно все ваше сообщение будет сохранено и, в последствии, будет использовано в качестве стартового сообщения')
    bot.register_next_step_handler(message, updateStartMessage)

def updateStartMessage(message):
    start_message = message.text
    file = open('start_message.txt', 'w', encoding='utf-8')
    file.write(start_message)
    file.close()
    bot.send_message(message.chat.id, 'Данные успешно сохранены')


@bot.callback_query_handler(func = lambda call: True)
def callback_quary(call):
    global user_id
    if call.data =='check_sub':
        if checkSubscribtion(user_id) == False:
            subscribeToChannels(call.message)
        else:
            sendMeUsername(call.message)

    elif call.data == 'admin_panel':
        adminPanel(call.message)

    elif call.data == 'update_groups':
        sendMeGroups(call.message)

    elif call.data == 'update_sheet':
        if dataToGoogleSheet() == True:
            bot.send_message(call.message.chat.id, 'Гугл таблица успешно обновлена')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка, попробуйте еще раз')

    elif call.data == 'change_start_message':
        sendMeStartMessage(call.message)

    elif call.data == 'ref_system':
        showRefSystem(call.message, user_id)

if __name__ == '__main__':
    bot.polling(none_stop=True)


