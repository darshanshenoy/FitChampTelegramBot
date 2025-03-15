from telegram import Update
import json
from telegram.ext import Application, CommandHandler, ContextTypes
import config
import google_auth
from google.oauth2.credentials import Credentials
import health_data
import sqlite3

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Use /auth to link your Google account, /health to fetch data, or /leaderboard to see the top steppers!")

# Command handler for /auth
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.message.from_user.id
    creds = google_auth.get_credentials(telegram_id)
    conn = sqlite3.connect("health_data.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (telegram_id, google_token) VALUES (?, ?)", 
              (telegram_id, creds.to_json()))
    conn.commit()
    conn.close()
    await update.message.reply_text("Google account linked successfully! Use /health to fetch your data.")

# Command handler for /health
async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.message.from_user.id
    conn = sqlite3.connect("health_data.db")
    c = conn.cursor()
    c.execute("SELECT google_token FROM users WHERE telegram_id = ?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    if result:
        creds = Credentials.from_authorized_user_info(json.loads(result[0]), google_auth.SCOPES)
        steps, calories, distance = health_data.fetch_health_data(telegram_id, creds)
        await update.message.reply_text(f"Steps: {steps}\nCalories: {calories:.2f}\nDistance: {distance:.2f} meters")
    else:
        await update.message.reply_text("Please link your Google account with /auth first.")

# Command handler for /leaderboard
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sqlite3.connect("health_data.db")
    c = conn.cursor()
    c.execute("SELECT telegram_id, SUM(steps) as total_steps FROM health_data GROUP BY telegram_id ORDER BY total_steps DESC LIMIT 5")
    leaders = c.fetchall()
    conn.close()
    leaderboard_text = "🏆 Leaderboard (Top 5 Steps):\n"
    for i, (telegram_id, steps) in enumerate(leaders, 1):
        user = await context.bot.get_chat(telegram_id)
        leaderboard_text += f"{i}. {user.user.first_name}: {steps} steps\n"
    await update.message.reply_text(leaderboard_text)

# Main function to set up and run the bot
def main():
    # Initialize the application with your bot token
    application = Application.builder().token(config.TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("auth", auth))
    application.add_handler(CommandHandler("health", health))
    application.add_handler(CommandHandler("leaderboard", leaderboard))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()