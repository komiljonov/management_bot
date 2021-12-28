import os
import requests
from telegram.ext import *
from telegram import *
from constants import *
from utils import *
from authenticate import authentication
from request_handler import *
from telegram.utils import helpers
import datetime
from decorators import *
import time

time.sleep(3)


def make_time_str(format: str = None):
    time = datetime.datetime.now()
    if format is not None:
        return time.strftime(format)
    return time.strftime("%d.%m.%Y %H:%M:%S")


def check_auth(callback: callable):
    def wrapper(update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
        except Exception as e:
            user = update.callback_query.from_user
        db_user = db.check_request_status(user.id)
        if db_user['status'] == None:
            context.user_data['greeting'] = update.message.reply_html(
                f"Assalomu alaykum {user.first_name}\n\n<b>Ismingizni kiriting!</b>", reply_markup=ReplyKeyboardRemove())
            return NAME
        else:
            return authentication.wait_start(update, context)
    return wrapper


class Bot(Updater):
    def __init__(self, token: str = None):
        assert token, ValueError("Token is required")
        super().__init__(token)

        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start), CallbackQueryHandler(
                    self.accept_request_admin, pattern="^accept_request"),
                CallbackQueryHandler(
                    self.deny_request_admin, pattern="^deny_request"),
                CallbackQueryHandler(
                    self.accept_request_from_user, pattern="^confirm_user_request"),
                CallbackQueryHandler(
                    self.deny_request_from_user, pattern="^deny_user_request"),
                MessageHandler(Filters.regex("^🔖 So'rov yuborish$"), self.send_request), MessageHandler(Filters.regex(
                    "^🕓 Kutilayotgan so'rovlar"), self.get_waiting_sent_requests), MessageHandler(Filters.regex("^💤 Tasdiqlanmagan so'rovlar"), self.unconfirmed_requests),
                MessageHandler(Filters.regex("^✔️ Tasdiqlangan so'rovlar$"),
                               self.confirmed_requests),
                MessageHandler(Filters.regex("^✖️ Rad etilgan so'rovlar$"),
                               self.denied_requests)
            ],
            states={
                NAME: [MessageHandler(Filters.text, authentication.name)],
                NUMBER: [MessageHandler(Filters.contact | Filters.regex("(?:\+[9]{2}[8][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2})"), authentication.number), ],
                # DESCRIPTION: [MessageHandler(Filters.text, authentication.description), ],
                WAIT: [CommandHandler('start', authentication.wait_start)],
                MENU: [MessageHandler(Filters.regex("^🔖 So'rov yuborish$"), self.send_request), MessageHandler(Filters.regex("^🕓 Kutilayotgan so'rovlar"), self.get_waiting_sent_requests), MessageHandler(Filters.regex("^💤 Tasdiqlanmagan so'rovlar"), self.unconfirmed_requests), MessageHandler(Filters.regex("^✔️ Tasdiqlangan so'rovlar$"), self.confirmed_requests), MessageHandler(Filters.regex("^✖️ Rad etilgan so'rovlar$"),
                                                                                                                                                                                                                                                                                                                                                                                           self.denied_requests)],
                SELECT_REQUEST_TYPE: [MessageHandler(Filters.regex('^◀️ ortga'), lambda update, context:self.start(update, context)), MessageHandler(Filters.text, send_request_handler.req_type), CommandHandler('cancel', send_request_handler.cancel_request_2)],
                GET_TEMPLATE: [MessageHandler(Filters.text, send_request_handler.get_template_text)],
                # SELECT_CONFIRMERS: [CallbackQueryHandler(send_request_handler.add_confirmer, pattern="^add_confirmer"), CallbackQueryHandler(send_request_handler.remove_confirmer, pattern="^remove_confirmer"), CallbackQueryHandler(send_request_handler.done_request, pattern="^done_request"), CallbackQueryHandler(send_request_handler.cancel_request, pattern="^cancel_request")],
                CHECK_REQUEST_TRUE_OR_FALSE: [CallbackQueryHandler(send_request_handler.confirm_request, pattern="^temp_accept_request_true"), CallbackQueryHandler(send_request_handler.error_request, pattern="^error_request_false"), MessageHandler(Filters.regex("^◀️ ortga"), self.back_from_confirm)],
                GET_COMMENT_FOR_REQUEST: [MessageHandler(
                    Filters.text, self.get_comment_for_request)],
                CONFIRMED_REQUESTS: [MessageHandler(Filters.regex("^kelgan so'rovlar$"), self.confirmed_come_requests), MessageHandler(
                    Filters.regex("^yuborilgan so'rovlar$"), self.confirmed_sent_requests)],
                DENIED_REQUESTS: [MessageHandler(Filters.regex("^kelgan so'rovlar$"), self.denied_come_requests), MessageHandler(
                    Filters.regex("^yuborilgan so'rovlar$"), self.denied_sent_requests)]
            },
            fallbacks=[CommandHandler('start', self.start), CallbackQueryHandler(self.accept_request_admin, pattern="^accept_request"),
                       CallbackQueryHandler(
                           self.deny_request_admin, pattern="^deny_request"),
                       CallbackQueryHandler(
                           self.accept_request_from_user, pattern="^confirm_user_request"),
                       CallbackQueryHandler(
                           self.deny_request_from_user, pattern="^deny_user_request"),
                       MessageHandler(Filters.regex("^🔖 So'rov yuborish$"), self.send_request), MessageHandler(Filters.regex("^🕓 Kutilayotgan so'rovlar"), self.get_waiting_sent_requests), MessageHandler(Filters.regex("^💤 Tasdiqlanmagan so'rovlar"), self.unconfirmed_requests)]
        )
        self.dispatcher.add_handler(self.conversation)
        self.dispatcher.add_handler(CommandHandler("data", self.data))
        self.dispatcher.add_handler(CommandHandler(
            'register_group', self.register_group))
        self.start_polling()
        print('polling')
        self.idle()

    def is_authed_decorator(function: callable):
        def wrapper(self: "Bot", update: Update, context: CallbackContext):
            try:
                user = update.message.from_user
            except:
                user = update.callback_query.from_user
            au = db.is_authed(user.id)
            if au:
                return function(self, update, context)
            else:
                # return self.conversation.handle_update(update, context.dispatcher, self.conversation.check_update(update), context)
                return self.start(update, context)
        return wrapper

    def start(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
        except:
            user = update.callback_query.from_user
        db_user = db.check_request_status(user.id)
        if db_user['status'] == None:
            if update.message.chat.type in ['supergroup', 'group']:
                update.message.reply_text("Iltimos botdan ro'yhatdan o'tish uchun quyodagi tugmani bosing👇", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Bo'tga o'tish!", url=helpers.create_deep_linked_url(context.bot.username, "register"))]]))
            else:
              		context.user_data['greeting'] = update.message.reply_html(f"""Assalomu alaykum <b>{user.first_name}</b>!\n\n<b>Ismingiz va familyangizni kiriting!</b>""", reply_markup=ReplyKeyboardRemove())
            return NAME
        else:
            if not len(context.args if not context.args == None else []) <= 1 and context.args[0] == 'get_description':
                update.message.reply_text("Iltimos fikringizni yozing!")
                return GET_COMMENT_FOR_REQUEST

            return authentication.wait_start(update, context)

    @is_authed_decorator
    def send_request(self, update: Update, context: CallbackContext):
        user = update.message.from_user
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

    @is_authed_decorator
    def accept_request_admin(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        db_user = db.check_request_status(user.id)
        if db_user:
            if db_user['is_admin']:
                res = db.accept_request_admin(db_user['id'], int(
                    update.callback_query.data.split(":")[1]))
                if res['ok']:
                    iddd = update.callback_query.data.split(":")[1]
                    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                        f"{cross} Rad etish", callback_data=f"deny_request:{iddd}")]])
                    reqqqq = msg_db.get_request(iddd)
                    messages = msg_db.get_messages(reqqqq[0][1])

                    db_req = db.get_request(iddd)['data']
                    name = db_req['name']
                    number = db_req['number']
                    username = db_req['username']
                    text = f"Tizimga kirish uchun so'rov tasdiqlandi!\n\n<b>ismi</b>: {name}\n<b>raqami</b>: {number}\n<b>username</b>: {username}\n<b>Tasdiqlovchi</b>: <a href=\"https://t.me{user.username}\">{user.first_name}</a>\n<b>Tasdiqlash vaqti:</b> {make_time_str()}"
                    for msg in messages:
                        msg_id = msg[2]
                        chat_id = msg[3]
                        context.bot.edit_message_text(
                            text, chat_id, msg_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                    context.bot.send_message(text="Sizga tizimga kirish uchun ruhsat berildi!",
                                             chat_id=db_req['chat_id'], reply_markup=keyboards.make_menu_keyboards())
                    # update.callback_query.message.edit_text(text, reply_markup=keyboard)

    @is_authed_decorator
    def deny_request_admin(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        db_user = db.check_request_status(user.id)
        data = update.callback_query.data.split(":")
        if db_user:
            if db_user['is_admin']:
                iddd = update.callback_query.data.split(":")[1]
                res = db.deny_request_admin(db_user['id'], int(iddd))
                if res['ok']:
                    db_req = db.get_request(iddd)['data']
                    name = db_req['name']
                    number = db_req['number']
                    username = db_req['username']

                    messages = msg_db.get_messages(iddd)

                    text = f"Tizimga kirish uchun so'rov bekor qilindi!\n<b>ismi</b>: {name}\n<b>raqami</b>: {number}\n<b>username</b>: {username}\n<b>Bekor qiluvchi</b>:  <a href=\"https://t.me{user.username}\">{user.first_name}</a>\n<b>Tasdiqlash vaqti:</b> {make_time_str()}\n\n"
                    for msg in messages:
                        msg_id = msg[2]
                        chat_id = msg[3]
                        context.bot.edit_message_text(
                            text, chat_id, msg_id, parse_mode=ParseMode.HTML)

                    context.bot.send_message(
                        text="Kechirasiz sizga tizimga kirish uchun ruhsat berilmadi!", chat_id=db_req['chat_id'])

    @is_authed_decorator
    def accept_request_from_user(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user

        req = db.get_request_from_user(user.id, int(
            update.callback_query.data.split(":")[1]))['data']
        sent_req = msg_db.get_request_2(req['id'])
        sent_msgs2 = msg_db.get_messages_2(sent_req[0][1])
        confers_text = ""

        if update.callback_query.message.chat.type == "private":
            for conf in req['req_type']['confirmers']:
                confers_text += f"{conf['name']}\n"

            text = f"<b>So'rov tasdiqlandi!</b>\n<b>So'rov raqami</b>: {req['id']}\n<b>so'rov turi</b>: {req['req_type']['name']}\n<b>shablon</b>:\n<b>-------------------------------</b>\n{req['template']}\n<b>-------------------------------</b>\n<b>tasdiqlovchilar</b>:\n<b>-------------------------------</b>\n\n{confers_text}\n<b>-------------------------------</b>\ntasdiqlovchi: {user.first_name} (@{user.username})"
            update_status = db.update_request_status(user.id, req['id'], 1)
            if update_status['ok']:
                for msg in sent_msgs2:
                    # context.bot.edit_message_text(text=text, chat_id=msg[3], chat_id=msg[2])
			try:
                    		context.bot.edit_message_text(text=text, chat_id=msg[3], message_id=msg[2], parse_mode=ParseMode.HTML).pin()
			except: pass
		context.bot.send_message(text=text, chat_id=req['user']['chat_id'], parse_mode=ParseMode.HTML).pin()
        else:
            if is_confirmer(req, user):
                for conf in req['req_type']['confirmers']:
                    confers_text += f"{conf['name']}\n"
                text = f"<b>So'rov tasdiqlandi!</b>\n<b>So'rov raqami</b>: {req['id']}\n<b>so'rov turi</b>: {req['req_type']['name']}\n<b>shablon</b>:\n<b>-------------------------------</b>\n{req['template']}\n<b>-------------------------------</b>\n<b>tasdiqlovchilar</b>:\n<b>-------------------------------</b>\n\n{confers_text}\n<b>-------------------------------</b>\ntasdiqlovchi: {user.first_name} (@{user.username})"
                update_status = db.update_request_status(user.id, req['id'], 1)
                if update_status['ok']:
                    
                    for msg in sent_msgs2:
                        try:
                            # context.bot.edit_message_text(text=text, chat_id=msg[3], chat_id=msg[2])
                            context.bot.edit_message_text(
                                text=text, chat_id=msg[3], message_id=msg[2], parse_mode=ParseMode.HTML)
                            context.bot.send_message(
                                text=text, chat_id=msg[3], parse_mode=ParseMode.HTML).pin()
                        except:
                            pass

                    try:
                        context.bot.send_message(text=text, chat_id=req['user']['chat_id'], parse_mode=ParseMode.HTML)
                    except:
                        pass
            else:
                update.callback_query.answer(
                    "Kechirasiz siz bu so'rov tasdiqlovchilar qatorida emassiz!", show_alert=True)

                # update.callback_query.message.reply_text("Kechirasiz siz bu so'rov tasdiqlovchilar qatorida emassiz!")

    @is_authed_decorator
    def deny_request_from_user(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        req = db.get_request_from_user(user.id, int(
            update.callback_query.data.split(":")[1]))['data']
        if update.callback_query.message.chat.type == "private":
            context.user_data['checked_request_status'] = 1
            context.user_data['checking_request'] = int(
                update.callback_query.data.split(":")[1])
            update.callback_query.message.reply_text(
                "Iltimos so'rov uchun fikringizni yozing!", reply_markup=ReplyKeyboardRemove())
            return GET_COMMENT_FOR_REQUEST
        else:
            if is_confirmer(req, user):
                context.user_data['checked_request_status'] = 1
                context.user_data['checking_request'] = int(
                    update.callback_query.data.split(":")[1])
                update.callback_query.message.reply_text("So'rovdagi kamchiliklarni yozish uchun bo'tga yozing!")
                return GET_COMMENT_FOR_REQUEST
            else:
                update.callback_query.answer(
                    "Kechirasiz siz bu so'rov tasdiqlovchilar qatorida emassiz!", show_alert=True)
                # update.callback_query.message.reply_text("Kechirasiz siz bu so'rov tasdiqlovchilar qatorida emassiz!")

    @is_authed_decorator
    def get_comment_for_request(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        keys = keyboards.make_menu_keyboards()
        req = db.get_request_from_user(
            user.id, context.user_data['checking_request'])
        req_db = db.get_request_from_user(user.id, req['data']['id'])['data']
        sent_req = msg_db.get_request_2(req['data']['id'])
        sent_msgs2 = msg_db.get_messages_2(sent_req[0][1])

        req = db.update_request_status(
            user.id, req_db['id'], 2, update.message.text)
        text = format_request_to_text(req['data'])

        error_users = []
        if req['ok']:
            

            for msg in sent_msgs2:
                # context.bot.edit_message_text(text=text, chat_id=msg[3], chat_id=msg[2])
                try:
                    context.bot.edit_message_text(text=text, chat_id=msg[3], message_id=msg[2], parse_mode=ParseMode.HTML)
                    context.bot.send_message(text=text, chat_id=msg[3], parse_mode=ParseMode.HTML).pin()
                except:
                    error_users.append(msg)



        update.message.reply_text(
            checkkkk[context.user_data['checked_request_status']], reply_markup=keys)
        return MENU

    @is_authed_decorator
    def get_waiting_sent_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_waiting_sent_requests(user.id)
        if reqs != None and reqs['ok'] and len(reqs['data']) > 0:
            for req in reqs['data']:
                confers_text = ""
                for coner in req['req_type']['confirmers']:
                    confers_text += f"{coner['name']} (@{coner['username']})\n"

                text = format_request_to_text(req)
                update.message.reply_text(text, parse_mode="HTML")
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=keyboards.make_menu_keyboards())
        return MENU

    @is_authed_decorator
    def unconfirmed_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_waiting_come_requests(user.id)
        if reqs != None and reqs['ok'] and any(isinstance(x, dict) for x in reqs['data']):
            if len(reqs['data']) > 0:
                for req in reqs['data']:
                    confers_text = ""
                    if req == None:
                        continue
                    text = format_request_to_text(req)
                    update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            f"{done} so'rovni tasdiqlash", callback_data=f"confirm_user_request:{req['id']}"),
                        InlineKeyboardButton(
                            f"{cross} so'rovni rad etish", callback_data=f"deny_user_request:{req['id']}")
                    ]]))
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=keyboards.make_menu_keyboards())
            return MENU

    def register_group(self, update: Update, context: CallbackContext):

        if update.message.chat.type in ['supergroup', 'group']:
            exists = db.get_group(update.message.chat.id)
            if not exists and exists == None:
                new_gr = db.register_group(
                    update.message.chat.id, update.message.chat.title)
                if new_gr['ok']:
                    update.message.reply_text("Guruh qo'shildi!")
                else:
                    update.message.reply_text("Guruh qo'shishda hatolik!")
            else:
                update.message.reply_text("Guruh allaqachon qo'shilgan!")
        else:
            update.message.reply_text(
                "Kechirasiz bu komanda faqat guruhda ishlatish mumkin!")

    def data(self, update: Update, context: CallbackContext):
        res = download_file(
            f"{host}/get_excel/", update.message.from_user.id)
        if res:
            file = open(res, 'rb')
            update.message.reply_document(file)
            os.remove(os.path.abspath(res))
        else:
            update.message.reply_text("Kechirasiz siz admin emassiz!")
        return MENU
            
    def confirmed_requests(self, update: Update, context: CallbackContext):
        update.message.reply_text("Kelgan so'rovlarmi yoki yuborilgan!", reply_markup=ReplyKeyboardMarkup([[
            "kelgan so'rovlar",
            "yuborilgan so'rovlar",
        ]], resize_keyboard=True))
        return CONFIRMED_REQUESTS

    def confirmed_come_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_confirmed_come_requests(user.id)
        if reqs != None and len(reqs['data']) > 0:
            for req in reqs['data']:
                confers_text = ""
                for coner in req['req_type'].get('confirmers', []):
                    if coner != {}:
                        confers_text += f"{coner['name']} @{coner['username']}"
                update.message.reply_text(
                    "Barcha kelgan va tasdiqlangan so'rovlar!", reply_markup=make_menu_keyboards())
                text = format_request_to_text(req)
                update.message.reply_text(text, parse_mode="HTML")
            return MENU
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=make_menu_keyboards())
            return MENU

    def confirmed_sent_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_confirmed_sent_requests(user.id)
        if reqs != None and len(reqs['data']) > 0:
            for req in reqs['data']:
                confers_text = ""
                for coner in req['req_type'].get('confirmers', []):
                    if coner != {}:
                        confers_text += f"{coner['name']} @{coner['username']}"
                text = format_request_to_text(req)
                update.message.reply_text(text, parse_mode="HTML")
            update.message.reply_text(
                "Barcha yuborilgan va tasdiqlangan so'rovlar!", reply_markup=make_menu_keyboards())
            return MENU
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=make_menu_keyboards())
            return MENU

    def denied_requests(self, update: Update, context: CallbackContext):
        update.message.reply_text("Kelgan so'rovlarmi yoki yuborilgan!", reply_markup=ReplyKeyboardMarkup([[
            "kelgan so'rovlar",
            "yuborilgan so'rovlar",
        ]], resize_keyboard=True))
        return DENIED_REQUESTS

    def denied_come_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_denied_come_requests(user.id)
        if reqs != None and len(reqs['data']) > 0:
            for req in reqs['data']:
                confers_text = ""
                for coner in req['req_type'].get('confirmers', []):
                    if coner != {}:
                        confers_text += f"{coner['name']} @{coner['username']}"
                text = format_request_to_text(req)
                update.message.reply_text(text, parse_mode="HTML")
            update.message.reply_text(
                "Barcha kelgan va rad etilgan so'rovlar!", reply_markup=make_menu_keyboards())
            return MENU
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=make_menu_keyboards())
            return MENU

    def denied_sent_requests(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        reqs = db.get_denied_sent_requests(user.id)
        if reqs != None and len(reqs['data']) > 0:
            for req in reqs['data']:
                confers_text = ""
                for coner in req['req_type'].get('confirmers', []):
                    if coner != {}:
                        confers_text += f"{coner['name']} @{coner['username']}"
                text = format_request_to_text(req)
                update.message.reply_text(text, parse_mode="HTML")
            update.message.reply_text(
                "Barcha yuborilgan va rad etilgan so'rovlar!", reply_markup=make_menu_keyboards())
            return MENU
        else:
            update.message.reply_text(
                "Kechirasiz hozircha so'rovlar yo'q!", reply_markup=make_menu_keyboards())
            return MENU

    def back_from_confirm(self, update: Update, context: CallbackContext):
        update.message.reply_text(f"<b>Iltimos so'rov malumotlarini to'g'irlab yuboring!</b>\n\n{context.user_data['req_type']['template'] if not None else ''}", reply_markup=ReplyKeyboardMarkup(
            [["◀️ ortga"]], resize_keyboard=True), parse_mode=ParseMode.HTML)
        return GET_TEMPLATE


bot = Bot(TOKEN)
