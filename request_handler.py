from telegram import replykeyboardremove
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from utils import *
from constants import *
from utils import keyboards
from telegram.utils import helpers
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
            update.message.reply_text("Iltimos shablonni yuboring text yoki fayl ko'rinishida!", reply_markup=replykeyboardremove.ReplyKeyboardRemove())
            return GET_TEMPLATE
        else:
            update.message.reply_text("Kechirasiz joriy so'rov turi topilmadi!")

    
    def get_template_text(self, update:Update, context:CallbackContext):
        user  = update.message.from_user
        req_template = update.message.text
        context.user_data['req_template'] = req_template
        keys = keyboards.make_users_keyboard(update, context)
        update.message.reply_text("Iltimos endi tasdiqlashi mumkin bo'lgan foydalanuvchuni tanlang!", reply_markup=keys)
        return SELECT_CONFIRMERS

    
    def add_confirmer(self, update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        data = update.callback_query.data.split(":")
        context.user_data['request_confirmers'].append(int(data[1]))
        keys = make_users_keyboard(update, context)
        update.callback_query.message.edit_text(text=update.callback_query.message.text,reply_markup=keys)


    def remove_confirmer(self, update:Update, context:CallbackContext):
        data = update.callback_query.data.split(":")
        context.user_data['request_confirmers'].remove(int(data[1]))
        keys = make_users_keyboard(update, context)
        update.callback_query.message.edit_text(text=update.callback_query.message.text, reply_markup=keys)

    def done_request(self,update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        request_type = context.user_data['req_type']
        request_template = context.user_data['req_template']
        request_confirmers = context.user_data['request_confirmers']
        update.callback_query.message.reply_text("Iltimos so'rov to'g'riligini tasdiqlang!")
        db.get_admins_by_list(request_confirmers, user.id)

        confers_text = ""
        for conf in db.get_admins_by_list(request_confirmers, user.id)['data']:
            url = helpers.create_deep_linked_url(conf['username'],"check-this-out",)
            confers_text += f"[{conf['name']}](t.me{url})\n"

        text = f"so'rov turi: {request_type['name']}\nshablon:\n{request_template}\n\ntasdiqlovchilar\n\n{confers_text}"
        update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{done} tasdiqlash", callback_data="temp_accept_request_true"),
            InlineKeyboardButton(f"{cross} bekor qilish", callback_data="error_request_false")
        ]]), parse_mode="MarkdownV2", disable_web_page_preview=True)
        return CHECK_REQUEST_TRUE_OR_FALSE

        # db.create_request(user.id,request_type, request_template, request_confirmers)
    
    def cancel_request(self,update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        keys = keyboards.make_menu_keyboards()
        update.message.reply_text("Sizning so'rovingiz bekor qilindi!", reply_markup=keys)
        return MENU
    

    def confirm_request(self, update:Update, context:CallbackContext):
        user = update.callback_query.from_user
        request_type = context.user_data['req_type']
        request_template = context.user_data['req_template']
        request_confirmers = context.user_data['request_confirmers']
        admins = db.get_admins_by_list(request_confirmers, user.id)
        confers_text = ""
        for conf in db.get_admins_by_list(request_confirmers, user.id)['data']:
            confers_text += f"{conf['name']}\n"
        
        text = f"so'rov turi: {request_type['name']}\nshablon:\n{request_template}\n\ntasdiqlovchilar\n\n{confers_text}"
        new_req = db.create_request(user.id, request_type['id'], request_template, request_confirmers)
        new_db_req = msg_db.create_request_2(new_req['data']['id'])

        for admin in admins['data']:
            msg_id = context.bot.send_message(text=f"Yangi so'rov!\n\n{text}\nyuboruvchi: {user.name}", chat_id=admin['chat_id'], reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"{done} so'rovni tasdiqlash", callback_data=f"confirm_user_request:{new_req['data']['id']}"),
                InlineKeyboardButton(f"{cross} so'rovni rad etish", callback_data=f"deny_user_request:{new_req['data']['id']}")
            ]]))
            print(new_db_req)

            msg_db.create_message_2(new_db_req[0][1], msg_id.message_id, admin['chat_id'])
        update.callback_query.message.reply_text("So'rovingiz yuborildi!")
        update.callback_query.message.reply_text(text)
        return CHECK_REQUEST_TRUE_OR_FALSE
    
    def error_request(self, update:Update, context:CallbackContext):
        context.user_data['req_type'] = None
        context.user_data['req_template'] = ""
        context.user_data['request_confirmers'] = []

        user = update.callback_query.message.from_user
        request_types = db.get_request_types(user.id)
        keys = ReplyKeyboardMarkup(distribute([ d['name'] for d in request_types['data'] ], 2), resize_keyboard=True)
        update.message.reply_text("Iltimos so'rov turini qaytadan tanlang!", reply_markup=keys)
        return SELECT_REQUEST_TYPE
        
        


send_request_handler = send_request_handler()