# import telegram library
# SOURCE: https://www.geeksforgeeks.org/create-a-telegram-bot-using-python/
"""
This will contain the API key we got from BotFather to specify in which bot we are adding functionalities to using our python code.
"""
from multiprocessing import get_logger
from telegram.ext.updater import Updater
"""
This will invoke every time a bot receives an update i.e. message or command and will send the user a message.
"""
from telegram.update import Update
"""
We will not use its functionality directly in our code but when we will be adding the dispatcher it is required (and it will work internally)
"""
from telegram.ext.callbackcontext import CallbackContext
"""
This Handler class is used to handle any command sent by the user to the bot, a command always starts with “/” i.e “/start”,”/help” etc.
"""
from telegram.ext.commandhandler import CommandHandler
from telegram.ext import RegexHandler
"""
This Handler class is used to handle any normal message sent by the user to the bot,
"""
from telegram.ext.messagehandler import MessageHandler
"""
This will filter normal text, commands, images, etc from a sent message.
"""
from telegram.ext.filters import Filters

import time

import logging
logging.basicConfig(filename="../bot/botlog.txt",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
logger = get_logger()
aktuelle_folge = {"Ludwig": "?", "Agnes": "3754"}
first_name_to_chat = {"Ludwig": None, "Agnes": None}
bot = None

def log_access(update, action):
    # access log
    access_log = open("../bot/access_log.txt", "a")
    current_time = time.localtime()
    access_log.write(time.strftime('%Y-%m-%d %H:%M:%S GMT', current_time) + " " + update.message.from_user.first_name + " queried bot with " + action + "\n")
    access_log.close()

# import web crawler
from bs4 import BeautifulSoup
import requests

def get_episode_url(folgennummer):
    url = "https://www.daserste.de/unterhaltung/soaps-telenovelas/sturm-der-liebe/videos/sturm-der-liebe-folge-" + folgennummer + "-video-100.html"
    if video_found(get_soup(url)):
        return url
    url = "https://www.daserste.de/unterhaltung/soaps-telenovelas/sturm-der-liebe/videos/sturm-der-liebe-folge-" + folgennummer + "-video-104.html"
    if video_found(get_soup(url)):
        return url
    return "Not Found"
"""    url = "https://mediathekviewweb.de/#query=Sturm der Liebe " + folgennummer
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup)
    return "https://pdvideosdaserste-a.akamaihd.net/int/2022/01/05/d976658c-b10a-44ca-93ab-8d71ce651183/JOB_9566_sendeton_960x540-50p-1600kbit.mp4"
    
"""


# telegram methods
  
def start(update: Update, context: CallbackContext):
    log_access(update, "start")
    update.message.reply_text(
        "Hi Agnes ☺️ Ich bin dein SturmBot und stehe dir in stürmischen Zeiten zur Seite, damit du nicht den Überblick verlierst... Tippe /help")

def help(update: Update, context: CallbackContext):
    log_access(update, "help")
    update.message.reply_text("Nutze /folge FOLGENNUMMER um den Link zu einer Folge zu bekommen")

def folge_id(update: Update, context: CallbackContext):
    folgennummer = update.message.text.replace('/folge_', '')
    process_folge(update, CallbackContext, folgennummer)
    log_access(update, "nächster folge " + folgennummer)

def video_found(soup):
    return not soup.find("title").contents[0] == "Fehlerseite 404 - ARD | Das Erste"

def get_soup(folgenlink):
    r = requests.get(folgenlink, headers=headers)
    return BeautifulSoup(r.text, 'html.parser')

def watch_info(update: Update, context: CallbackContext):
    text = "Hier siehst du wer gerade bei welcher Folge ist:\n\n"
    for name in aktuelle_folge.keys():
        text+= name + ": Folge " + aktuelle_folge[name] + "\n" 
    update.message.reply_text(text)
    log_access(update, "watch info")

def test_for_match(update: Update, context: CallbackContext):
    if aktuelle_folge["Ludwig"] == aktuelle_folge["Agnes"]:
        time.sleep(4.5)
        if first_name_to_chat["Agnes"]:
            bot.send_message(chat_id=first_name_to_chat["Agnes"].id, text="🎊")
            bot.send_message(chat_id=first_name_to_chat["Agnes"].id, text="Hey Agnes, du und Ludwig sind gerade bei derselben Folge. Wollt ihr die nächste zusammenschauen?\n\n(YEEAH ☺️ It's a match.)")
        if first_name_to_chat["Ludwig"]:
            bot.send_message(chat_id=first_name_to_chat["Ludwig"].id, text="🎊")
            bot.send_message(chat_id=first_name_to_chat["Ludwig"].id, text="Hey Ludwig, du und Agnes sind gerade bei derselben Folge. Wollt ihr die nächste zusammenschauen?\n\n(YEEAH ☺️ It's a match.)")



def process_folge(update: Update, context: CallbackContext, folgennummer):
    if str.isnumeric(folgennummer):
        folgenlink = get_episode_url(folgennummer)
        if folgenlink != "Not Found":
            soup = get_soup(folgenlink)
            description = soup.find("meta", {"name": "twitter:description"})["content"]
            title = soup.find("meta", {"name": "twitter:title"})["content"]
            image_url = soup.find("meta", {"name": "twitter:image:src"})["content"]
            update.message.reply_text("Folge " + folgennummer + "? Klaro, hier ist der Link zur Folge: \n \n " + folgenlink +"\n \n Viel Vergnügen 😘")
            update.message.reply_text(title + "\n\n" + description + "\n\n" + "Dein Link zur nächsten Folge: /folge_"+str(int(folgennummer) + 1))
            first_name = update.message.from_user.first_name
            aktuelle_folge[first_name] = folgennummer
            first_name_to_chat[first_name] = update.message.chat
            test_for_match(update, context)
        else:
            update.message.reply_text("Schande... 🙄 Die Folge habe ich nicht in meiner Datenbank.")
    else:
        update.message.reply_text("Ich bin voll verwirrt... Ist " + folgennummer + " wirklich eine Zahl?")


def folge(update: Update, context: CallbackContext):
    folgennummer = update.message.text[7:]
    process_folge(update, CallbackContext, folgennummer)
    log_access(update, "folge " + folgennummer)
    
headers = {'user-agent': 'sdltelegrambridgebot_2022'}
telegram_bot_token = open("../bot/telegram_bot_token", "r").read().replace("\n","")
updater = Updater(telegram_bot_token,
                  use_context=True)
bot = updater.bot

updater.dispatcher.add_handler(CommandHandler('folge', folge))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(RegexHandler('^(/folge_[\d]+)$', folge_id))
updater.dispatcher.add_handler(RegexHandler('^([\d]+)$', folge_id))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('watch_info', watch_info))
updater.start_polling()



