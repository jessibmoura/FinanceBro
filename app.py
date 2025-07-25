from utils.utils import *

import telebot
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
users = {}

bot = telebot.TeleBot(TOKEN) # type: ignore

@bot.message_handler(commands=['start'])
def first_contact(message):
    """ Asks user for name and welcomes them """
    chat_id = message.chat.id
    bot.send_message(chat_id, """What’s up, legend? Name’s Finance Bro — your personal CFO, hype man, and accountability partner on the road to obscene wealth.\n 
I’m here to 10x your net worth, optimize your hustle, and make sure your wallet stays as jacked as your gym routine.\n\nBut before we start stacking wins... what should I call the next big player in this market?""")
    bot.register_next_step_handler(message,welcoming)

def welcoming(message):
    """ Gives a warm welcoming to user by calling them the name they gave before. """
    chat_id = message.chat.id
    name = message.text.strip()
    users[chat_id] = name
    bot.send_message(chat_id,f""" Lock it in, {name}.\nWe’re about to dominate this savings game like it’s earnings season.\nNo lattes, no liabilities — just pure, uncut capital gains. Let’s build that war chest, bro 💼🔥""")


@bot.message_handler(commands=['hello'])
def hello(message):
    """ Message asking if user needs help """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Yo {users[chat_id]}, talk to me. What’s the play, bro?")

@bot.message_handler(commands=['out'])
def expense(message):
    """ Message to register a new income value """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Logging a new capital outflow, bro? What are we tagging this one as? ")
    bot.register_next_step_handler(message, process_expense)

def process_expense(message):
    """ Extracts the information necessary from the message """
    chat_id = message.chat.id
    expense_message = message.text.strip() # <expense: float> blank-space <description: str optional> blank-space <category: str>

    try:
        float_value, description, category = parse_message(expense_message)
        send_date = datetime.now().strftime('%d/%m/%Y')

        register = {
            "value": float_value,
            "description": description,
            "category": category,
            "date": send_date
        }
        print(f"Register: {register}")

        bot.send_message(chat_id, f"""So, what I'm getting is:\n\n 📅 Date: {send_date}\n💰 Value: {float_value}\n📝 Description: {description or '(No description)'}\n🏷️ Category: {category}\n\nIs that right? [Y/N]""")
        bot.register_next_step_handler(message, reprocess_expense)
    except Exception as e:
        bot.send_message(chat_id, f"Oops! There was an error processing your input: \n>{e}\nPlease try again.")
        bot.register_next_step_handler(message, process_expense)  # tenta de novo

def reprocess_expense(message):
    chat_id = message.chat.id
    status = message.text.strip()

    if status.upper() == 'N':
        bot.send_message(chat_id, f"Can you try sending the message again?")
        bot.register_next_step_handler(message, process_expense)
    elif status.upper() == 'Y':
        bot.send_message(chat_id, f"Alright champ! Expense registered. 💸")


print("Bot running...")
bot.infinity_polling()
