import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag_proccesor import RAGProcessor
from chef_pipeline import run_chef_agent
from agent import process_inventory_message
from google import genai
from pypdf import PdfReader

client = genai.Client()

#LOAD ENV VARIABLES
load_dotenv()
TELEGRAM_TOKEN= os.getenv("TELEGRAM_TOKEN")

# --- BOOT UP THE GLOBAL BRAIN ---
print("Booting up the Global Chef Brain (Reading PDF)...")
global_processor = RAGProcessor()
# We do this out here so it only happens ONCE when you start the script!
reader = PdfReader("recipes/Recetas.pdf")
full_text = "".join([page.extract_text() + " " for page in reader.pages])
global_processor.add_to_index(full_text)
print("Brain loaded! Ready for Telegram.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers the /start command."""
    await update.message.reply_text("Hello ! I'm your AI chef. Send me your inventory updates or ask for a recipe!")


def get_intent(user_text: str) -> str:
    """Uses Gemini to classify the user's message."""
    
    # [YOUR TURN: Write a strict prompt. Tell the AI it is a router. 
    # Explain what an "INVENTORY" message looks like and what a "RECIPE" message looks like.
    # CRITICAL: Tell it to ONLY output the word INVENTORY or RECIPE, with no other text.]
    prompt = f"""
    You are a strict AI Router. Your job is to choose between 2 tools, if you are going to add or remove elements from the inventory or if
    you are going to give a recipe 
        
        CRITICAL RULES:
        1. Your output must ONLY be one word. Choose between "INVENTORY" or "RECIPE" nothing else.
        2. the judgment to choose the word "INVENTORY": if the user is talking about: he bought, grabbed, took, used, cooked, every word that is related to take or use something 
        3. the judgment to choose the word "RECIPE": if the user feels or want to do: something, hunger, confussion, boredom, cooking, making.
    
    User message: {user_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite', 
        contents=prompt
    )
    # We use .strip().upper() to remove any invisible spaces and make it uppercase!
    return response.text.strip().upper()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_user = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    print(f"\nRecieved message: {message_user}")

    intent = get_intent(message_user)
    print(f"Router classified message as: {intent}")

    if "INVENTORY" in intent:
        reply = process_inventory_message(message_user)

    elif "RECIPE" in intent:
        reply = run_chef_agent(message_user, global_processor)

    else:

        reply = "I'm sorry, I am just a Chef! I only handle inventory updates and recipe requests."

    await update.message.reply_text(reply)



def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running. Press Ctrl + C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()