from telegram.ext import *
from telegram import *
from constants import *
from utils import *
from authenticate import authentication


class Bot(Updater):
    def __init__(self, token: str = None):
        assert token, ValueError("Token is required")
        super().__init__(token)

        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start)
            ],
            states={
                NAME: [MessageHandler(Filters.text, authentication.name)],
                NUMBER: [MessageHandler(Filters.contact | Filters.regex("(?:\+[9]{2}[8][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2})"), authentication.number), ],
                DESCRIPTION: [MessageHandler(Filters.text, authentication.description), ],
                WAIT: [CommandHandler('start', authentication.wait_start)],
                MENU: [MessageHandler(Filters.regex(
                    "^So'rob yuborish$"), self.send_request)]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.accept_request_admin, pattern="^accept_request"))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.deny_request_admin, pattern="^deny_request"))
        self.dispatcher.add_handler(self.conversation)
        self.start_polling()
        print('polling')
        self.idle()

    def start(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        db_user = db.check_request_status(user.id)
        if db_user == None:
            update.message.reply_text(
                "Assalomu alaykum bo'timizga xush kelibsiz!\nSiz bizning bo'timizdan ro'yxatdan o'tishingiz lozim!\nIltimos ism va familyangizni yozing!\nMison uchun:\n    Komiljonvo Shukurullox")
            return NAME
        else:
            return authentication.wait_start(update, context)

    def send_request(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        request_types = db.get_request_types()
        keyboard = distribute(request_statuses, 2)

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
                        f"{cross} Rad etish", callback_data=f"accept_request:{iddd}")]])
                    reqqqq = msg_db.get_request(iddd)
                    messages = msg_db.get_messages(reqqqq[0][1])

                    for msg in messages:
                        print(msg)
                    
                    update.callback_query.message.edit_text(f"Tizimga kirish uchun so'rov bekor qilindi!\n{update.callback_query.message.text[34:]}", reply_markup=keyboard)


    def deny_request_admin(self, update: Update, context: CallbackContext):
        user = update.callback_query.from_user
        db_user = db.check_request_status(user.id)
        if db_user:
            if db_user['is_admin']:
                iddd = update.callback_query.data.split(":")[1]
                res = db.deny_request_admin(db_user['id'], int(iddd))
                if res['ok']:
                    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                        f"{done} Ruhsat berish", callback_data=f"accept_request:{iddd}")]])
                    messages = msg_db.get_messages(iddd)
                    for msg in messages:
                        print(msg)

                    update.callback_query.message.edit_text(
                        f"Tizimga kirish uchun so'rov bekor qilindi!\n{update.callback_query.message.text[34:]}", reply_markup=keyboard)




bot = Bot(TOKEN)