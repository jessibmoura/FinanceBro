from utils.utils import *
from utils.images import *
from database.firestore import FirestoreDB

import telebot
from dotenv import load_dotenv
import pendulum
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN) # type: ignore
db = FirestoreDB()
USUARIO_CACHE = {}

@bot.message_handler(commands=['hello'])
def first_contact(message):
    """ Asks user for name and welcomes them """
    chat_id = message.chat.id
    
    if db.check_user(chat_id):
        name = db.user_collection.document(str(chat_id)).get().to_dict().get("name")
        USUARIO_CACHE[chat_id] = name
        bot.send_message(chat_id, f"Sup {name}, my legend! 🔥")
    else:
        bot.send_message(chat_id, """What’s up, legend? Name’s Finance Bro — your personal CFO, hype man, and accountability partner on the road to obscene wealth.\n 
I’m here to 10x your net worth, optimize your hustle, and make sure your wallet stays as jacked as your gym routine.\n\nBut before we start stacking wins... let me get to know you! Please tell me info below:\n\n Name\nMonthly Income (it can be a estimation)\nSavings Target (0 if you don't have it)""")
        bot.register_next_step_handler(message,welcoming)

def welcoming(message):
    """ Gives a warm welcoming to user by calling them the name they gave before. """
    chat_id = message.chat.id
    welcome_message = message.text.strip()
    # Gets information about user
    name, mon_income_flt, save_target_flt = parse_start_message(welcome_message)

    user = {
        "name": name,
        "monthly_income": mon_income_flt,
        "savings_target": save_target_flt
    }

    USUARIO_CACHE[chat_id] = name
    if db.create_user(chat_id, user):
        bot.send_message(chat_id,f""" Lock it in, {name}.\nWe’re about to dominate this savings game like it’s earnings season.\nNo lattes, no liabilities — just pure, uncut capital gains. Let’s build that war chest, bro 💼🔥""")


@bot.message_handler(commands=['out'])
def expense(message):
    """ Message to register a new expense value """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Logging a new capital outflow, bro? What are we tagging this one as? ")
    bot.register_next_step_handler(message, process_expense)

@bot.message_handler(commands=['in'])
def income(message):
    """ Message to register a new income value """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Yooo made some extra money?? Tell me all about it!")
    bot.register_next_step_handler(message, process_income)

def process_income(message):
    """ Extracts the information necessary from the message """
    
    chat_id = message.chat.id
    income_message = message.text.strip() # <income: float> \n <description: str optional>

    try:
        float_value, description = parse_income_message(income_message)
        send_date = pendulum.now().format("DD/MM/YYYY")

        register = {
            "value": float_value,
            "description": description,
            "date": send_date
        }
        print(f"Register: {register}")

        bot.send_message(chat_id, f"""So, what I'm getting is:\n\n 📅 Date: {send_date}\n💰 Value: {float_value}\n📝 Description: {description or '(No description)'}\n\nIs that right? [Y/N]""")
        bot.register_next_step_handler(message, reprocess_income)
    except Exception as e:
        bot.send_message(chat_id, f"Oops! There was an error processing your input: \n>{e}\nPlease try again.")
        bot.register_next_step_handler(message, process_income)

def reprocess_income(message):
    chat_id = message.chat.id
    status = message.text.strip()

    if status.upper() == 'N':
        bot.send_message(chat_id, f"Can you try sending the message again?")
        bot.register_next_step_handler(message, process_income)
    elif status.upper() == 'Y':
        bot.send_message(chat_id, f"Good job! Income registered. 💸")

def process_expense(message):
    """ Extracts the information necessary from the message """
    chat_id = message.chat.id
    expense_message = message.text.strip() # <expense: float> \n <description: str optional> \n <category: str>

    try:
        float_value, description, category, date = parse_expense_message(expense_message)

        register = {
            "chat_id":chat_id,
            "value": float_value,
            "description": description,
            "category": category,
            "date": date
        }
        print(f"Register: {register}")

        bot.send_message(chat_id, f"""So, what I'm getting is:\n\n 📅 Date: {date}\n💰 Value: {float_value}\n📝 Description: {description or '(No description)'}\n🏷️ Category: {category}\n\nIs that right? [Y/N]""")
        bot.register_next_step_handler(message, reprocess_expense, register)
    except Exception as e:
        bot.send_message(chat_id, f"Oops! There was an error processing your input: \n>{e}\nPlease try again.")
        bot.register_next_step_handler(message, process_expense) 

def reprocess_expense(message, register: dict):
    chat_id = message.chat.id
    status = message.text.strip()

    if status.upper() == 'N':
        bot.send_message(chat_id, f"Can you try sending the message again?")
        bot.register_next_step_handler(message, process_expense)
    elif status.upper() == 'Y':
        db.insert_expense(chat_id=chat_id,information=register)
        bot.send_message(chat_id, f"Ok champ... Expense registered... Let's try to not spend all of our money away. 💸")
        bot.send_sticker(chat_id, expense_id_sticker())

# @bot.message_handler(content_types=['sticker'])
# def pegar_file_id(message):
#     print("File ID da figurinha:", message.sticker.file_id)
#     bot.reply_to(message, f"File ID: {message.sticker.file_id}")

print("Bot running...")
bot.infinity_polling()
