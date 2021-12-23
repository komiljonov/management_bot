
from utils import *
from constants import *
from utils import keyboards
from telegram import *
from telegram.ext import *
done = "✅"
prev = "⏮"
next = "⏭"
comment = "💬"
cross = "❌"
trash = "🗑"
reload = "🔄"



class send_request_handler:
    def req_type(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        req_type_name = update.message.text
        req_type = db.get_req_type(user.id, req_type_name)
        context.user_data['request_confirmers'] = []
        if req_type is not None:
            context.user_data['req_type'] = req_type
            update.message.reply_text(f"<b>Iltimos so'rov malumotlarini to'g'irlab yuboring!</b>\n\n{req_type['template'] if not None else ''}", reply_markup=ReplyKeyboardMarkup([["◀️ ortga"]], resize_keyboard=True), parse_mode=ParseMode.HTML)
            return GET_TEMPLATE
        else:
            update.message.reply_text("Kechirasiz joriy so'rov turi topilmadi!")

    
    def get_template_text(self, update:Update, context:CallbackContext):
        user  = update.message.from_user
        req_template = update.message.text
        context.user_data['req_template'] = req_template
        if req_template == "◀️ ortga":
            request_types = db.get_request_types(user.id)
            if len(request_types['data']):
                keys = ReplyKeyboardMarkup(distribute(
                    [d['name'] for d in request_types['data']], 2) + [[f"◀️ ortga"]], resize_keyboard=True)
                update.message.reply_text(
                    "So'rov turini tanlang!", reply_markup=keys)
                return SELECT_REQUEST_TYPE
            else:
                update.message.reply_text(
                    "Kechirasiz hozircha hechqanday so'rov turi mavjud emas!", reply_markup=keyboards.make_menu_keyboards())
                return MENU
        if update.message.text == "/cancel" or update.message.text == "/start":
            return self.cancel_request_2(update, context)
        
        user = update.message.from_user
        request_type = context.user_data['req_type']
        request_template = context.user_data['req_template']
        update.message.reply_text("Iltimos so'rov to'g'riligini tasdiqlang!")
        db.get_admins_by_list(request_type['confirmers'], user.id)

        confers_text = ""
        for conf in request_type['confirmers']:
            confers_text += f"{conf['name']} (@{conf['username']})\n"

        text = f"<b>so'rov turi</b>: {request_type['name']}\n<b>shablon:</b>\n<b>-------------------------------</b>\n{request_template}\n<b>-------------------------------</b>\n<b>tasdiqlovchilar</b>\n\n{confers_text}"
        context.user_data['confirm_request_msgmsg'] =  update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{done} tasdiqlash", callback_data="temp_accept_request_true"),
            InlineKeyboardButton(f"{cross} bekor qilish", callback_data="error_request_false")
        ]]), disable_web_page_preview=True, parse_mode=ParseMode.HTML)
        return CHECK_REQUEST_TRUE_OR_FALSE

        # db.create_request(user.id,request_type, request_template, request_confirmers)
    
    def cancel_request(self,update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        keys = keyboards.make_menu_keyboards()
        update.callback_query.message.reply_text("Sizning so'rovingiz bekor qilindi!", reply_markup=keys)
        return MENU
    

    def confirm_request(self, update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        request_type = context.user_data['req_type']
        request_template = context.user_data['req_template']
        confers_text = ""




        for conf in request_type['confirmers']:
            confers_text += f"{conf['name']} (@{conf['username']})\n"
        
        new_req = db.create_request(user.id, request_type['id'], request_template)
        new_db_req = msg_db.create_request_2(new_req['data']['id'])
        text = format_request_to_text(new_req['data'])

        for admin in request_type['confirmers']:
            try:
                msg_id = context.bot.send_message(text=f"<b>Yangi so'rov!</b>\n\n{text}\nyuboruvchi: {user.name}", chat_id=admin['chat_id'], reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"{done} so'rovni tasdiqlash", callback_data=f"confirm_user_request:{new_req['data']['id']}"),
                    InlineKeyboardButton(f"{cross} so'rovni rad etish", callback_data=f"deny_user_request:{new_req['data']['id']}")
                ]]), parse_mode=ParseMode.HTML)
                msg_db.create_message_2(new_db_req[0][1], msg_id.message_id, admin['chat_id'])
            except Exception as e:
                print(e)

        
        for admin in request_type['groups']:
            try:
                msg_id = context.bot.send_message(text=f"<b>Yangi so'rov!</b>\n\n{text}\nyuboruvchi: {user.name}", chat_id=admin['chat_id'], reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"{done} so'rovni tasdiqlash", callback_data=f"confirm_user_request:{new_req['data']['id']}"),
                    InlineKeyboardButton(f"{cross} so'rovni rad etish", callback_data=f"deny_user_request:{new_req['data']['id']}")
                ]]), parse_mode=ParseMode.HTML)
                msg_db.create_message_2(new_db_req[0][1], msg_id.message_id, admin['chat_id'])
            except Exception as e:
                print(e)

        context.user_data['confirm_request_msgmsg'].delete()



        user.send_message("So'rovingiz yuborildi!")
        msg_id = user.send_message(text, parse_mode=ParseMode.HTML, reply_markup=keyboards.make_menu_keyboards())
        msg_db.create_message_2(new_db_req[0][1], msg_id.message_id, user.id)
        return MENU
        
    
    def error_request(self, update:Update, context:CallbackContext):
        context.user_data['req_type'] = None
        context.user_data['req_template'] = ""
        user = update.callback_query.message.from_user
        request_types = db.get_request_types(user.id)
        keys = ReplyKeyboardMarkup(distribute(
                [d['name'] for d in request_types['data']], 2) + [[f"◀️ ortga"]], resize_keyboard=True)
        update.callback_query.message.reply_text("Iltimos so'rov turini qaytadan tanlang!", reply_markup=keys)
        context.user_data['confirm_request_msgmsg'].delete()
        return SELECT_REQUEST_TYPE
    
    def cancel_request_2(self, update:Update, context:CallbackContext):
        context.user_data['req_type'] = None
        context.user_data['req_template'] = ""
        update.message.reply_text("Bosh menu", reply_markup=keyboards.make_menu_keyboards())
        return MENU


send_request_handler = send_request_handler()