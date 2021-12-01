from telegram.ext import *
from telegram import *
from utils import *
from constants import *

class _Authentication:
    def name(self, update:Update, context:CallbackContext):
        context.user_data['name'] = update.message.text
        update.message.reply_text("Iltimos endi raqamingizni yuboring!", reply_markup=send_number_keyboard())
        return NUMBER
    
    def number(self, update:Update, context:CallbackContext):
        context.user_data['number'] = update.message.text or update.message.contact.phone_number
        update.message.reply_text("Iltimos endi o'zingiz haqingizdagi malumotlarni text ko'rinishida yuboring!\nAdmin bu malumotlarni o'qiydi va sizga bo'tga kirish uchun ruxsat beradi!", reply_markup=send_number_keyboard())
        return DESCRIPTION
    def description(self, update:Update, context:CallbackContext):
        db.request_authorization(update.message.from_user.id, context.user_data['name'], update.message.text, context.user_data['number'], update.message.from_user.username)
        update.message.reply_text("Sizning so'rovingiz qabul qilindi!\nRuhsat berilganda o'zimiz malum qilamiz!\nAgarda uzoq vaqt habar kelmasa /start kommandasini yuboring!")
        return WAIT
    

    def wait_start(self, update:Update, context:CallbackContext):
        res = db.check_request_status(update.message.from_user.id)
        if res in (0,2):
            update.message.reply_text(f"Sizning so'rovingiz {request_statuses[res]}!")
        elif res == 1:
            update.message.reply_text("Sizning so'rovingiz qabul qilindi!")
            return MENU
        else:
            update.message.reply_text("Kechirasiz sizning so'rovingiz topilmadi!\nIltimos qayra ro'yxatdan o'ting!")
            return self.name(update,context)

        

authentication = _Authentication()