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
        update.message.reply_text("Iltimos endi o'zingiz haqingizdagi malumotlarni text ko'rinishida yuboring!\nAdmin bu malumotlarni o'qiydi va sizga bo'tga kirish uchun ruxsat beradi!", reply_markup=ReplyKeyboardRemove())
        return DESCRIPTION

    def description(self, update:Update, context:CallbackContext):
        name = context.user_data['name']
        number = context.user_data['number']
        username = update.message.from_user.username
        user_id = update.message.from_user.id
        res = db.request_authorization(user_id, name, update.message.text, number, username)
        if res['ok']:
            update.message.reply_text("Sizning so'rovingiz qabul qilindi!\nRuhsat berilganda o'zimiz malum qilamiz!\nAgarda uzoq vaqt habar kelmasa /start kommandasini yuboring!")
            admins = db.get_admins_list(update.message.from_user.id)
            req = msg_db.create_request(res['rq_id'])
            text = f"Tizimga kirish uchun so'rov noma!\nismi: {name}\nraqami: {number}\nusername: {username}"
            keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{done} Ruhsat berish", callback_data=f"accept_request:{res['rq_id']}"), InlineKeyboardButton(f"{cross} rad etish" , callback_data=f"deny_request:{res['rq_id']}")
            ]])

            for admin in admins:
                try:
                    msg_id = context.bot.send_message(text=text, chat_id=admin['chat_id'], reply_markup=keyboard)
                    msg_db.create_message(req[0][1], msg_id.message_id, admin['chat_id'])
                except Exception as e: print(e)
        return WAIT
    

    def wait_start(self, update:Update, context:CallbackContext):
        res = db.check_request_status(update.message.from_user.id)
        if res['status'] == 0:
            update.message.reply_text(f"Sizning so'rovingiz {request_statuses[res['status']]}!", reply_markup=ReplyKeyboardRemove())
        elif res['status'] == 2:
            update.message.reply_text(f"Sizning so'rovingiz {request_statuses[res['status']]}!", reply_markup=ReplyKeyboardRemove())
        elif res['status'] == 1:
            update.message.reply_text("Sizning so'rovingiz qabul qilindi!", reply_markup=ReplyKeyboardRemove())
            return MENU
        else:
            update.message.reply_text("Kechirasiz sizning so'rovingiz topilmadi!\nIltimos qayta ro'yxatdan o'ting!\nIsmingizni yuboring!", reply_markup=ReplyKeyboardRemove())
            return NAME

        

authentication = _Authentication()
