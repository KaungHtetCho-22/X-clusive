from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from db import User, Group, Expense, get_db
from sqlalchemy.orm import Session
import datetime
import openai
import json

# Set your OpenAI API key
openai.api_key = "A"

# Initialize database session
db_session = next(get_db())

# Function to extract expense details using OpenAI
def extract_expense_details(user_input):
    prompt = f"""
    Extract the following details from the user's message:
    - Amount (e.g., $50)
    - Category (e.g., food, travel)
    - Participants (e.g., Alice, Bob)

    User's message: "{user_input}"

    Return the details in JSON format with keys: amount, category, participants.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts expense details from user messages."},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        extracted_data = response.choices[0].message.content
        return json.loads(extracted_data)
    except Exception as e:
        print(f"Error parsing OpenAI response: {e}")
        return None

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    user = db_session.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        user = User(telegram_id=user_id, name=user_name)
        db_session.add(user)
        db_session.commit()

    await update.message.reply_text(f"Welcome, {user_name}! Use /add to log an expense or /report to view summaries.")

# Command: /add
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = db_session.query(User).filter(User.telegram_id == user_id).first()

    if not user:
        await update.message.reply_text("Please use /start to register first.")
        return

    user_input = update.message.text

    try:
        extracted_data = extract_expense_details(user_input)
        if not extracted_data:
            await update.message.reply_text("Sorry, I couldn't understand that. Please try again.")
            return

        amount = extracted_data.get("amount")
        category = extracted_data.get("category")
        participants = extracted_data.get("participants", [])

        if not amount or not category:
            await update.message.reply_text("Sorry, I couldn't extract the amount or category. Please try again.")
            return

        expense = Expense(amount=amount, category=category, payer_id=user.id, date=datetime.datetime.now())
        db_session.add(expense)
        db_session.commit()

        await update.message.reply_text(f"Expense added: ${amount} for {category} with {', '.join(participants)}.")
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Something went wrong. Please try again later.")

# Command: /report
async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = db_session.query(User).filter(User.telegram_id == user_id).first()

    if not user:
        await update.message.reply_text("Please use /start to register first.")
        return

    expenses = db_session.query(Expense).filter(Expense.payer_id == user.id).all()

    if not expenses:
        await update.message.reply_text("No expenses found.")
        return

    total_spent = sum(expense.amount for expense in expenses)
    categories = {}
    for expense in expenses:
        categories[expense.category] = categories.get(expense.category, 0) + expense.amount

    report = f"Total spent: ${total_spent:.2f}\n"
    for category, amount in categories.items():
        report += f"{category}: ${amount:.2f}\n"

    await update.message.reply_text(report)

# Main function to run the bot
def main():
    application = ApplicationBuilder().token("waef").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))
    application.add_handler(CommandHandler("report", generate_report))

    application.run_polling()

if __name__ == "__main__":
    main()