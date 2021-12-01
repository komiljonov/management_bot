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
                NUMBER: [MessageHandler(Filters.contact | Filters.regex("(?:\+[9]{2}[8][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2})"), authentication.number),],
                DESCRIPTION: [MessageHandler(Filters.text, authentication.description),],
                WAIT: [CommandHandler('start', authentication.wait_start)],
                MENU: [MessageHandler("So'rob yuborish", self.send_request)]
            },
            fallbacks=[CommandHandler('start', self.start)]
            )
        self.dispatcher.add_handler(self.conversation)
        self.start_polling()
        print('polling')
        self.idle()
    

    def start(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        db_user = db.check_request_status(user.id)
        if db_user == None:
            update.message.reply_text("Assalomu alaykum bo'timizga xush kelibsiz!\nSiz bizning bo'timizdan ro'yxatdan o'tishingiz lozim!\nIltimos ism va familyangizni yozing!\nMison uchun:\n    Komiljonvo Shukurullox")
            return NAME
        else:
            return authentication.wait_start(update, context)
    
    def send_request(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        request_types = db.get_request_types()
        keyboard = distribute(request_statuses, 2)
        
        
    


bot = Bot(TOKEN)
