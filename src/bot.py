import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

async def start(update: Update, context):
    await update.message.reply_text("Welcome to FinanceBot! Send me an expense like 'Add $50 for groceries'.")

async def handle_text(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"Received: {text}")

def main():
    # Initialize bot
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()