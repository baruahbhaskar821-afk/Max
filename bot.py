#!/usr/bin/env python3
"""
MAX BOT - Full AI Bot with Google Gemini (New SDK)
Python 3.14 Compatible - No Errors!
"""

import json
import time
import re
import os
import random
from datetime import datetime
from threading import Thread
from flask import Flask, request
import requests

# ========== NEW GEMINI SDK (Python 3.14 Compatible) ==========
from google import genai
from google.genai import types

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YAHAN_APNA_TOKEN_DALO")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YAHAN_APNI_GEMINI_KEY_DALO")
BOT_NAME = "Max"

# Initialize Gemini Client (New SDK)
if GEMINI_API_KEY and GEMINI_API_KEY != "YAHAN_APNI_GEMINI_KEY_DALO":
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI (New SDK) initialized!")
else:
    GEMINI_AVAILABLE = False
    print("⚠️ No Gemini API key - using fallback mode")

# ========== FLASK APP ==========
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🤖 Max Bot with FULL Gemini AI is Running! ✅"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update:
            process_update(update)
        return 'OK', 200
    except Exception as e:
        print(f"Webhook Error: {e}")
        return 'Error', 500

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, threaded=True)

# ========== TELEGRAM FUNCTIONS ==========
def send_message(chat_id, text, parse_mode='Markdown', reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {'chat_id': chat_id, 'text': text[:4096]}
    if parse_mode:
        params['parse_mode'] = parse_mode
    if reply_markup:
        params['reply_markup'] = reply_markup
    try:
        requests.post(url, json=params, timeout=30)
    except Exception as e:
        print(f"Send error: {e}")

def edit_message(chat_id, message_id, text, parse_mode='Markdown', reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    params = {'chat_id': chat_id, 'message_id': message_id, 'text': text[:4096]}
    if parse_mode:
        params['parse_mode'] = parse_mode
    if reply_markup:
        params['reply_markup'] = reply_markup
    try:
        requests.post(url, json=params, timeout=30)
    except Exception as e:
        print(f"Edit error: {e}")

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={'callback_query_id': callback_id}, timeout=30)
    except Exception as e:
        print(f"Callback error: {e}")

def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    try:
        requests.post(url, json={'chat_id': chat_id, 'action': 'typing'}, timeout=30)
    except Exception as e:
        print(f"Typing error: {e}")

def get_bot_info():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                username = data['result'].get('username')
                print(f"✅ Bot connected: @{username}")
                return True
    except Exception as e:
        print(f"Get bot info error: {e}")
    return False

# ========== FULL AI RESPONSE WITH GEMINI (NEW SDK) ==========
def get_ai_response(user_message, user_name):
    """Get response from Gemini AI using new SDK"""
    
    if not GEMINI_AVAILABLE:
        return fallback_response(user_message, user_name)
    
    try:
        # Create prompt
        prompt = f"""Tu {BOT_NAME} hai, ek friendly aur smart assistant. User ka naam {user_name} hai.

Rules:
1. Hinglish mein jawab de (Hindi + English mix)
2. Short aur simple rakhe (max 2-3 lines)
3. Agar calculation ho toh calculate kar
4. Agar nahi pata toh seedha bol de "Mujhe nahi pata"
5. Friendly aur helpful ban

User question: {user_message}

Answer:"""
        
        # New SDK way - using generate_content
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return "⚠️ Kuch gadbad ho gayi. Dobara poocho!"
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return fallback_response(user_message, user_name)

def fallback_response(user_message, user_name):
    """Fallback when Gemini is unavailable"""
    
    msg = user_message.lower().strip()
    
    # Simple calculations
    calc_result = calculate_math(msg)
    if calc_result:
        return calc_result
    
    # Simple Q&A
    qa_pairs = {
        'hello': f"Namaste {user_name}! 👋 Kaise ho?",
        'hi': f"Hi {user_name}! 🤗 Kya help chahiye?",
        'how are you': f"Main theek hoon {user_name}! 😊 Aap batao?",
        'thanks': f"Welcome {user_name}! 😊",
        'time': f"Current time: {datetime.now().strftime('%I:%M %p')} ⏰",
        'date': f"Today: {datetime.now().strftime('%d %B %Y')} 📅",
        'who are you': f"Main {BOT_NAME} hoon! AI assistant 🤖",
        'what can you do': f"Calculation, GK, Coding Help, Translation, Chat! 🎯",
        'joke': "Santa: Banta teri shirt ke kitne button hain?\nBanta: 4!\nSanta: Nahi, 6 hain!\nBanta: Main 4 gin raha hoon, tum extra 2 kahan se la rahe ho? 😂",
    }
    
    for key, answer in qa_pairs.items():
        if key in msg:
            return answer
    
    return f"Main samjha nahi {user_name}. Kuch aur poocho! 🧮 Example: '2+2' ya 'Python kya hai?'"

def calculate_math(text):
    """Calculate math expressions"""
    patterns = [
        (r'(\d+)\s*\+\s*(\d+)', lambda a, b: a + b),
        (r'(\d+)\s*-\s*(\d+)', lambda a, b: a - b),
        (r'(\d+)\s*\*\s*(\d+)', lambda a, b: a * b),
        (r'(\d+)\s*/\s*(\d+)', lambda a, b: a / b if b != 0 else None),
    ]
    
    for pattern, operation in patterns:
        match = re.search(pattern, text)
        if match:
            a = int(match.group(1))
            b = int(match.group(2))
            result = operation(a, b)
            if result is not None:
                if isinstance(result, float) and result != int(result):
                    return f"🧮 = {result:.2f}"
                else:
                    return f"🧮 = {int(result)}"
    return None

# ========== KEYBOARDS ==========
def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🤖 AI Chat", "callback_data": "menu_ai"}],
            [{"text": "📚 Help", "callback_data": "menu_help"}],
            [{"text": "ℹ️ About", "callback_data": "menu_about"}],
            [{"text": "🔧 Features", "callback_data": "menu_features"}],
            [{"text": "⚡ Status", "callback_data": "menu_stats"}]
        ]
    }

def get_back_button():
    return {
        "inline_keyboard": [
            [{"text": "🔙 Back to Main Menu", "callback_data": "main_menu"}]
        ]
    }

def get_features_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🧮 Calculator", "callback_data": "feature_calc"}],
            [{"text": "💻 Coding Help", "callback_data": "feature_code"}],
            [{"text": "📚 General Knowledge", "callback_data": "feature_gk"}],
            [{"text": "🌐 Translation", "callback_data": "feature_translate"}],
            [{"text": "✍️ Writing Help", "callback_data": "feature_write"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }

# ========== HELP TEXTS ==========
def get_help_text():
    ai_status = "✅ ACTIVE" if GEMINI_AVAILABLE else "⚠️ FALLBACK MODE"
    return f"""
🤖 *{BOT_NAME} - Full AI Bot*

*🧠 AI Status:* {ai_status}

*📌 Commands:*
/start - Start bot
/help - This menu

*💬 How to use:*
• Group mein: `{BOT_NAME} sawaal`
• Private mein: Direct message

*✨ Examples:*
• "2+2 kya hai?"
• "Python mein loop kaise likhen?"
• "Taj Mahal kisne banaya?"
• "Good morning ka hindi"
• "Ek joke sunao"
• "Mujhe motivation chahiye"

*🎯 AI Features:*
✅ Smart Conversations
✅ Calculations
✅ Coding Help
✅ General Knowledge
✅ Translation
✅ Writing Help
✅ Jokes & Fun
"""

def get_about_text():
    return f"""
📖 *About {BOT_NAME}*

🤖 *Name:* {BOT_NAME}
🧠 *AI Model:* Google Gemini 2.0 Flash
🎯 *Type:* Full AI Assistant
💬 *Language:* Hinglish
🆓 *Price:* Free Forever

*Features:*
• Full AI Conversations
• Smart Responses
• 24/7 Online
• Group + Private Chat

*Status:* 🟢 Active
"""

def get_stats_text():
    ai_status = "🟢 Gemini AI Active" if GEMINI_AVAILABLE else "🟡 Fallback Mode"
    return f"""
📊 *{BOT_NAME} Stats*

✅ Status: Active
🤖 Bot Name: {BOT_NAME}
🧠 AI Model: Gemini 2.0 Flash
{ai_status}

*Features:*
✅ Full AI Chat
✅ Smart Conversations
✅ Real-time Responses

*Limits:*
🆓 Unlimited messages
🌍 Global access
📱 Mobile friendly

*Ready to help! 🚀*
"""

def get_features_text():
    return """
🔧 *Features of {BOT_NAME}*

1️⃣ *🧮 Calculator*
   • Math expressions
   • Percentage calculations

2️⃣ *💻 Coding Help*
   • Python, JavaScript, HTML
   • Code explanations

3️⃣ *📚 General Knowledge*
   • History, Science, Geography
   • Current affairs

4️⃣ *🌐 Translation*
   • Any language
   • Hinglish support

5️⃣ *✍️ Writing Help*
   • Essays, stories, letters
   • Grammar check

*Try now!* Type any question! 🚀
"""

# ========== CALLBACK HANDLER ==========
def handle_callback_query(callback_query):
    callback_id = callback_query.get('id')
    message = callback_query.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    data = callback_query.get('data', '')
    
    answer_callback(callback_id)
    
    if data == 'main_menu':
        edit_message(chat_id, message_id,
                    f"🤖 *{BOT_NAME} - Main Menu*\n\nKya karna chahte ho?",
                    reply_markup=get_main_keyboard())
    
    elif data == 'menu_help':
        edit_message(chat_id, message_id, get_help_text(), reply_markup=get_back_button())
    
    elif data == 'menu_about':
        edit_message(chat_id, message_id, get_about_text(), reply_markup=get_back_button())
    
    elif data == 'menu_stats':
        edit_message(chat_id, message_id, get_stats_text(), reply_markup=get_back_button())
    
    elif data == 'menu_features':
        edit_message(chat_id, message_id, "🔧 *Features Menu*\n\nSelect an option:",
                    reply_markup=get_features_keyboard())
    
    elif data == 'menu_ai':
        edit_message(chat_id, message_id,
                    "🤖 *AI Chat Mode*\n\nBas apna sawaal likho! Main jawab dunga.\n\n✨ Examples:\n• 2+2 kya hai?\n• Python kya hai?\n• Ek joke sunao\n• Good morning ka hindi\n\nKuch bhi poocho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_calc':
        edit_message(chat_id, message_id,
                    "🧮 *Calculator*\n\nExamples:\n• 2+2 = 4\n• 10*5 = 50\n• 100/2 = 50\n\nBas calculation likho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_code':
        edit_message(chat_id, message_id,
                    "💻 *Coding Help*\n\nExamples:\n• 'Python mein loop kaise likhen?'\n• 'Function kaise banayein?'\n\nApna code ya question bhejo!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_gk':
        edit_message(chat_id, message_id,
                    "📚 *General Knowledge*\n\nExamples:\n• 'Taj Mahal kisne banaya?'\n• 'Moon par kab gaya tha?'\n\nKuch bhi poocho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_translate':
        edit_message(chat_id, message_id,
                    "🌐 *Translation*\n\nExamples:\n• 'Good morning ka hindi kya hai?'\n\nJo bhi translate karna hai poocho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_write':
        edit_message(chat_id, message_id,
                    "✍️ *Writing Help*\n\nExamples:\n• 'Mujhe ek story likhni hai'\n• 'Essay on pollution'\n\nBatao kya likhna hai?",
                    reply_markup=get_back_button())

# ========== MESSAGE PROCESSING ==========
def should_reply(message):
    chat_type = message.get('chat', {}).get('type')
    message_text = message.get('text', '').lower()
    
    if chat_type == 'private':
        return True
    if BOT_NAME.lower() in message_text:
        return True
    reply_to = message.get('reply_to_message')
    if reply_to and reply_to.get('from', {}).get('is_bot'):
        return True
    return False

def clean_message(text):
    if not text:
        return None
    text = re.sub(rf'\b{BOT_NAME}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[@＠][a-zA-Z0-9_]+', '', text)
    text = text.strip()
    return text if text else None

def process_update(update):
    # Handle button clicks
    if 'callback_query' in update:
        handle_callback_query(update['callback_query'])
        return
    
    # Handle messages
    message = update.get('message')
    if not message:
        return
    
    chat_id = message.get('chat', {}).get('id')
    chat_type = message.get('chat', {}).get('type')
    user_name = message.get('from', {}).get('first_name', 'User')
    username = message.get('from', {}).get('username', '')
    message_text = message.get('text', '')
    
    if not chat_id or not message_text:
        return
    
    # Handle commands
    if message_text.startswith('/'):
        cmd = message_text.lower().split()[0]
        if cmd == '/start':
            send_message(chat_id,
                        f"👋 Namaste {user_name}! Main {BOT_NAME} hoon with FULL Gemini AI!\n\nNeeche buttons use karo! 🔽",
                        reply_markup=get_main_keyboard())
            return
        elif cmd == '/help':
            send_message(chat_id, get_help_text(), reply_markup=get_back_button())
            return
        else:
            return
    
    # Check if should reply
    if not should_reply(message):
        return
    
    # Clean message
    cleaned = clean_message(message_text)
    if not cleaned:
        send_message(chat_id,
                    f"👋 Haan {user_name}! Main {BOT_NAME} yahan hoon.\n\nSawaal likho!",
                    reply_markup=get_main_keyboard())
        return
    
    # Show typing
    send_typing(chat_id)
    
    # Get AI response
    response = get_ai_response(cleaned, user_name)
    
    # Format for group
    if chat_type != 'private' and username:
        response = f"🤖 @{username}\n{response}"
    
    # Send response
    send_message(chat_id, response, reply_markup=get_back_button())
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {user_name}: {cleaned[:50]}...")

# ========== WEBHOOK & POLLING ==========
def set_webhook():
    render_url = os.environ.get("RENDER_URL", "")
    if not render_url:
        print("⚠️ RENDER_URL not set, using polling mode...")
        return False
    
    webhook_url = f"{render_url}/webhook"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
        time.sleep(1)
        response = requests.post(api_url, json={'url': webhook_url})
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ Webhook set: {webhook_url}")
                return True
    except Exception as e:
        print(f"Webhook error: {e}")
    return False

def polling_mode():
    print("🔄 Starting polling mode...")
    last_update_id = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            params = {'timeout': 30, 'allowed_updates': ['message', 'callback_query']}
            if last_update_id:
                params['offset'] = last_update_id + 1
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    for update in data['result']:
                        last_update_id = update['update_id']
                        process_update(update)
            
            time.sleep(1)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

# ========== MAIN ==========
def main():
    print("=" * 60)
    print(f"🤖 {BOT_NAME} BOT with FULL Gemini AI (New SDK)")
    print("=" * 60)
    
    if TELEGRAM_TOKEN == "YAHAN_APNA_TOKEN_DALO":
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        return
    
    if not get_bot_info():
        print("❌ Failed to connect to Telegram!")
        return
    
    # Start Flask
    Thread(target=run_flask, daemon=True).start()
    print(f"✅ Flask server started")
    
    # Start bot
    if not set_webhook():
        print("⚠️ Using polling mode...")
        polling_mode()
    else:
        print("✅ Bot is running with webhook!")
        print("=" * 60)
        print(f"🎯 {BOT_NAME} is LIVE with FULL AI!")
        if GEMINI_AVAILABLE:
            print("🧠 AI Model: Google Gemini 2.0 Flash")
        else:
            print("⚠️ No API Key - using fallback mode")
        print("💬 Send /start in Telegram")
        print("=" * 60)
        
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
