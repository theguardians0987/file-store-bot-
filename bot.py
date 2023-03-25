import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Set MongoDB URL
MONGODB_URL = os.environ.get('MONGODB_URL')

# Connect to MongoDB
client = MongoClient(MONGODB_URL)
db = client['filestore']
collection = db['files']

# Define start command
def start(update, context):
    """Send a welcome message when the command /start is issued."""
    update.message.reply_text('Hi! Send me any file and I will store it for you.')

# Define file handler
def file_handler(update, context):
    """Handle any file sent to the bot."""
    # Get file details
    file = update.message.document
    file_id = file.file_id
    file_name = file.file_name
    
    # Download file
    file_path = context.bot.get_file(file_id).download()
    
    # Store file in MongoDB
    with open(file_path, 'rb') as f:
        file_data = f.read()
    collection.insert_one({'file_name': file_name, 'file_data': file_data})
    
    # Reply with success message
    update.message.reply_text(f'Successfully stored file {file_name}.')

# Define error handler
def error(update, context):
    """Log errors caused by updates."""
    logging.warning(f'Update {update} caused error {context.error}.')

# Define main function
def main():
    """Start the bot."""
    # Create Updater and pass in the bot token
    updater = Updater(token=os.environ.get('TELEGRAM_BOT_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))

    # Register message handlers
    dispatcher.add_handler(MessageHandler(Filters.document, file_handler))

    # Register error handler
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    logging.info('Bot started')

    # Run the bot until Ctrl-C is pressed or the process is stopped
    updater.idle()

if __name__ == '__main__':
    main()
