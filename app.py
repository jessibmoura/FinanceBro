import telebot
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
users = {}

bot = telebot.TeleBot(TOKEN) # type: ignore

@bot.message_handler(commands=['start'])
def first_contact(message):
    """ Asks user for name and welcomes them """
    chat_id = message.chat.id
    bot.send_message(chat_id, """Hey there! I'm Finance Bro and my objective is to help you with your finance life. I hope you and I can do a great work together! :)\n
                     First things first, how can I call you?""")
    bot.register_next_step_handler(message,welcoming)

def welcoming(message):
    """ Gives a warm welcoming to user by calling them the name they gave before. """
    chat_id = message.chat.id
    name = message.text.strip()
    users[chat_id] = name
    bot.send_message(chat_id,f""" Nice,{name}! Let's save some money bro 🤖💰""")


@bot.message_handler(commands=['hello'])
def hello(message):
    """ Message asking if user needs help """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Yo {users[chat_id]}, how can i help you bro?")

print("Bot running...")
bot.infinity_polling()
