from telegram import *

def send_number_keyboard() -> ReplyMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(text="📞 raqamni yuborish", request_contact=True)]], resize_keyboard=True)
