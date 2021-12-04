from requests.models import parse_url
from telegram.ext import *
from telegram import *
from constants import *
from utils import *
from authenticate import authentication
from request_handler import *
from telegram.utils import helpers
import datetime


def make_time_str(format: str = None):
    time = datetime.datetime.now()
    if format is not None:
        return time.strftime(format)
    return time.strftime("%d.%m.%Y %H:%M:%S")


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
                    self.deny_request_from_user, pattern="^deny_user_request")
            ],
            states={
                NAME: [MessageHandler(Filters.text, authentication.name)],
                NUMBER: [MessageHandler(Filters.contact | Filters.regex("(?:\+[9]{2}[8][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2})"), authentication.number), ],
                DESCRIPTION: [MessageHandler(Filters.text, authentication.description), ],
                WAIT: [CommandHandler('start', authentication.wait_start)],
                MENU: [MessageHandler(Filters.regex(
                    "^So'rov yuborish$"), self.send_request)],
                SELECT_REQUEST_TYPE: [MessageHandler(Filters.text, send_request_handler.req_type)],
                GET_TEMPLATE: [MessageHandler(Filters.text, send_request_handler.get_template_text)],
                SELECT_CONFIRMERS: [CallbackQueryHandler(send_request_handler.add_confirmer, pattern="^add_confirmer"), CallbackQueryHandler(send_request_handler.remove_confirmer, pattern="^remove_confirmer"), CallbackQueryHandler(send_request_handler.done_request, pattern="^done_request"), CallbackQueryHandler(send_request_handler.cancel_request, pattern="^cancel_request")],
                CHECK_REQUEST_TRUE_OR_FALSE: [CallbackQueryHandler(send_request_handler.confirm_request, pattern="^temp_accept_request_true"), CallbackQueryHandler(send_request_handler.error_request, pattern="^error_request_false")],
                GET_COMMENT_FOR_REQUEST: [MessageHandler(
                    Filters.text, self.get_comment_for_request)]
            },
            fallbacks=[CommandHandler('start', self.start), CallbackQueryHandler(self.accept_request_admin, pattern="^accept_request"),
                       CallbackQueryHandler(
                           self.deny_request_admin, pattern="^deny_request"),
                       CallbackQueryHandler(
                           self.accept_request_from_user, pattern="^confirm_user_request"),
                       CallbackQueryHandler(self.deny_request_from_user, pattern="^deny_user_request")]
        )
        # self.dispatcher.add_handler(CallbackQueryHandler(self.accept_request_admin, pattern="^accept_request"))
        # self.dispatcher.add_handler(CallbackQueryHandler(self.deny_request_admin, pattern="^deny_request"))
        # self.dispatcher.add_handler(CallbackQueryHandler(self.accept_request_from_user, pattern="^confirm_user_request"))
        # self.dispatcher.add_handler(CallbackQueryHandler(self.deny_request_from_user, pattern="^deny_user_request"))
        self.dispatcher.add_handler(self.conversation)
        self.start_polling()
        print('polling')
        self.idle()

    def start(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        db_user = db.check_request_status(user.id)
        if db_user['status'] == None:
            update.message.reply_text(
                "Assalomu alaykum bo'timizga xush kelibsiz!\nSiz bizning bo'timizdan ro'yxatdan o'tishingiz lozim!\nIltimos ism va familyangizni yozing!\nMison uchun:\n    Komiljonvo Shukurullox", reply_markup=ReplyKeyboardRemove())
            return NAME
        else:
            return authentication.wait_start(update, context)

    def send_request(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        request_types = db.get_request_types(user.id)
        keys = ReplyKeyboardMarkup(distribute(
            [d['name'] for d in request_types['data']], 2), resize_keyboard=True)
        update.message.reply_text("So'rov turini tanlang!", reply_markup=keys)
        return SELECT_REQUEST_TYPE

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

                    # url = helpers.create_deep_linked_url(context.bot.username, user.username)
                    text = f"Tizimga kirish uchun so'rov tasdiqlandi!\n\nismi: {name}\nraqami: {number}\nusername: {username}\nTasdiqlovchi: <a href=\"https://t.me{user.username}\">{user.first_name} {make_time_str()} </a>"

                    for msg in messages:
                        msg_id = msg[2]
                        chat_id = msg[3]
                        context.bot.edit_message_text(
                            text, chat_id, msg_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                    # update.callback_query.message.edit_text(text, reply_markup=keyboard)

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

                    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                        f"{done} Ruhsat berish", callback_data=f"accept_request:{iddd}")]])
                    messages = msg_db.get_messages(iddd)

                    text = f"Tizimga kirish uchun so'rov bekor qilindi!\nismi: {name}\nraqami: {number}\nusername: {username}\nBekor qiluvchi:  <a href=\"https://t.me{user.username}\">{user.first_name}</a> {make_time_str()}\n\n"
                    for msg in messages:
                        msg_id = msg[2]
                        chat_id = msg[3]
                        context.bot.edit_message_text(
                            text, chat_id, msg_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    def accept_request_from_user(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        context.user_data['checked_request_status'] = 0
        context.user_data['checking_request'] = int(
            update.callback_query.data.split(":")[1])
        update.callback_query.message.reply_text(
            "Iltimos so'rov uchun fikringizni yozing!", reply_markup=ReplyKeyboardRemove())
        return GET_COMMENT_FOR_REQUEST

    def deny_request_from_user(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        context.user_data['checked_request_status'] = 1
        context.user_data['checking_request'] = int(
            update.callback_query.data.split(":")[1])
        update.message.reply_text(
            "Iltimos so'rov uchun fikringizni yozing!", reply_markup=ReplyKeyboardRemove())
        return GET_COMMENT_FOR_REQUEST

    def get_comment_for_request(self, update: Update, context: CallbackContext):
        print("Komment qabul qilindi!")
        user = update.message.from_user
        keys = keyboards.make_menu_keyboards()
        req = db.get_request_from_user(
            user.id, context.user_data['checking_request'])
        if context.user_data['checked_request_status'] == 0:
            print(req['data']['id'])
            sent_req = msg_db.get_request_2(req['data']['id'])
            sent_msgs = msg_db.get_messages_2(sent_req[0])

            for msg in sent_msgs:
                print(msg)
        else:
            pass

        update.message.reply_text(
            checkkkk[context.user_data['checked_request_status']], reply_markup=keys)
        return MENU


bot = Bot(TOKEN)


# I can help you create and manage Telegram bots. If you're new to the Bot API, please see the manual (https://core.telegram.org/bots).

# You can control me by sending these commands:

# /newbot - create a new bot
# /mybots - edit your bots [beta]

# Edit Bots
# /setname - change a bot's name
# /setdescription - change bot description
# /setabouttext - change bot about info
# /setuserpic - change bot profile photo
# /setcommands - change the list of commands
# /deletebot - delete a bot

# Bot Settings
# /token - generate authorization token
# /revoke - revoke bot access token
# /setinline - toggle inline mode
#  (https://core.telegram.org/bots/inline)/setinlinegeo - toggle inline location requests
#  (https://core.telegram.org/bots/inline#location-based-results)/setinlinefeedback - change inline feedback (https://core.telegram.org/bots/inline#collecting-feedback) settings
# /setjoingroups - can your bot be added to groups?
# /setprivacy - toggle privacy mode (https://core.telegram.org/bots#privacy-mode) in groups

# Games
# /mygames - edit your games (https://core.telegram.org/bots/games) [beta]
# /newgame - create a new game
#  (https://core.telegram.org/bots/games)/listgames - get a list of your games
# /editgame - edit a game
# /deletegame - delete an existing game
