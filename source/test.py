import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TB_TOKEN")
CHAT_ID = os.getenv("TB_CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# Erstelle eine Inline-Tastatur mit einem Hamburger-Icon
menu_markup = InlineKeyboardMarkup(row_width=1)
menu_button = InlineKeyboardButton("☰ Menü", callback_data='menu')
menu_markup.add(menu_button)

# Wenn der Benutzer /start eingibt, sendet der Bot eine Nachricht mit der Inline-Tastatur
@bot.message_handler(commands=['start'])
def send_menu(message):
    bot.send_message(message.chat.id, "Willkommen! Hier ist das Menü:", reply_markup=menu_markup)

# Wenn der Benutzer auf das Hamburger-Icon klickt, wird das Menü geöffnet
@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def open_menu(call):
    # Hier können Sie den Code für das Öffnen des Menüs einfügen
    pass

bot.polling()