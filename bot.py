#!/usr/bin/env python3
"""
MAX BOT - Google Gemini AI Version
Free, Fast, and Reliable!
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
import google.generativeai as genai

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YAHAN_APNA_TOKEN_DALO")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YAHAN_APNI_GEMINI_KEY_DALO")
BOT_NAME = "Max"

# ========== INITIALIZE GEMINI ==========
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free model

# ========== FLASK APP ==========
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🤖 Max Bot with Gemini AI is Running! ✅"

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
        response = requests.post(url, json=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Send error: {e}")
        return None

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

# ========== GEMINI AI RESPONSE ==========
def get_gemini_response(user_message, user_name, chat_history=None):
    try:
        # Create prompt in Hinglish
        prompt = f"""Tu {BOT_NAME} hai, ek friendly aur helpful assistant. User ka naam {user_name} hai.

Rules:
1. Hinglish mein jawab de (Hindi + English mix)
2. Short aur simple rakhe
3. Agar calculation ho toh calculate kar
4. Agar nahi pata toh seedha bol de "Mujhe nahi pata"
5. Friendly aur helpful ban

User question: {user_message}

Tera jawab:"""
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "⚠️ Kuch gadbad ho gayi. Dobara poocho!"
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        
        # Fallback responses if Gemini fails
        fallback_responses = [
            f"Sorry {user_name}, thodi der baad try karo! Technical issue hai. 🛠️",
            f"Yeh lo {user_name}, main thoda busy hoon. Thodi der mein aata hoon! ⏰",
            f"Arre {user_name}! Thoda ruko, aata hoon. 🤖",
            f"Kya pooch rahe ho {user_name}? Thoda clear karo! 😅"
        ]
        return random.choice(fallback_responses)

# ========== KEYBOARDS ==========
def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🤖 AI Chat", "callback_data": "menu_ai"}],
            [{"text": "📚 Help", "callback_data": "menu_help"}],
            [{"text": "ℹ️ About", "callback_data": "menu_about"}],
            [{"text": "🔧 Features", "callback_data": "menu_features"}],
            [{"text": "📊 Stats", "callback_data": "menu_stats"}]
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
            [{"text": "📚 GK", "callback_data": "feature_gk"}],
            [{"text": "🌐 Translation", "callback_data": "feature_translate"}],
            [{"text": "✍️ Writing", "callback_data": "feature_write"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }

# ========== HELP TEXTS ==========
def get_help_text():
    return f"""
🤖 *{BOT_NAME} - Help Menu*

*📌 Commands:*
/start - Bot start karo
/help - Yeh help menu

*💬 Group Mein:*
Sirf *{BOT_NAME}* likho aur sawaal poocho
Example: `Max 2+2 kya hai?`

*💬 Private Mein:*
Direct message karo ya neeche buttons use karo!

*🔧 AI Features (Gemini):*
• Calculations
• General knowledge
• Coding help
• Translation
• Writing help
• Friendly chat

*✨ Examples:*
• "2+2 kya hai?"
• "Python mein loop kaise likhen?"
• "Taj Mahal kisne banaya?"
• "Good morning ka hindi kya hai?"
• "Ek joke sunao"

*🎯 Free & Unlimited!*
"""

def get_about_text():
    return f"""
📖 *About {BOT_NAME}*

🤖 *Name:* {BOT_NAME}
🧠 *AI Model:* Google Gemini 1.5 Flash
🎯 *Type:* Smart Assistant
💬 *Language:* Hinglish
🆓 *Price:* Free Forever

*Features:*
• Gemini AI (Latest model)
• Instant responses
• 24/7 online
• Group + Private chat

*Why Gemini?*
✅ Free to use
✅ Fast responses
✅ Accurate answers
✅ Supports Hindi/English

*Created with:* ❤️
"""

def get_stats_text():
    return f"""
📊 *{BOT_NAME} Stats*

✅ Status: Active
🤖 Bot Name: {BOT_NAME}
🧠 AI Model: Gemini 1.5 Flash
⏰ Uptime: 24/7
💬 Language: Hinglish

*Features:*
✅ AI Chat (Gemini)
✅ Calculations
✅ General Knowledge
✅ Coding Help
✅ Translation
✅ Interactive Menu

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
   • 2+2, 10*5, sqrt(144)
   • Percentage calculations

2️⃣ *💻 Coding Help*
   • Python, JavaScript, HTML
   • Code explanations & debugging

3️⃣ *📚 General Knowledge*
   • History, Science, Geography
   • Current affairs

4️⃣ *🌐 Translation*
   • Any language to any language
   • Hinglish support

5️⃣ *✍️ Writing Help*
   • Essays, stories, letters
   • Grammar check

*How to use:*
Simply type your question!
Example: "Python kya hai?"
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
                    f"🤖 *{BOT_NAME} - Main Menu*\n\nKya karna chahte ho? Neeche se choose karo!",
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
                    "🤖 *AI Chat Mode (Gemini)*\n\nBas apna sawaal likho! Main jawab dunga.\n\n✨ Examples:\n• 2+2 kya hai?\n• Python kya hai?\n• Ek joke sunao\n• Good morning ka hindi\n\nKuch bhi poocho!",
                    reply_markup=get_back_button())
    
    # Features
    elif data == 'feature_calc':
        edit_message(chat_id, message_id,
                    "🧮 *Calculator Mode*\n\nExamples:\n• 2+2 = 4\n• 10*5 = 50\n• 100/2 = 50\n• 2^10 = 1024\n\nBas calculation likho! Jaise: '25*4 kya hai?'",
                    reply_markup=get_back_button())
    
    elif data == 'feature_code':
        edit_message(chat_id, message_id,
                    "💻 *Coding Help Mode*\n\nExamples:\n• 'Python mein loop kaise likhen?'\n• 'Function kaise banayein?'\n• 'Mujhe ek calculator program chahiye'\n\nApna code ya question bhejo!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_gk':
        edit_message(chat_id, message_id,
                    "📚 *General Knowledge Mode*\n\nExamples:\n• 'Taj Mahal kisne banaya?'\n• 'Moon par kab gaya tha?'\n• 'Computer ka invention kisne kiya?'\n\nKuch bhi poocho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_translate':
        edit_message(chat_id, message_id,
                    "🌐 *Translation Mode*\n\nExamples:\n• 'Good morning ka hindi kya hai?'\n• 'Bonjour ka matlab kya hai?'\n• 'Pyar ko english mein kya bolte hain?'\n\nJo bhi translate karna hai poocho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_write':
        edit_message(chat_id, message_id,
                    "✍️ *Writing Help Mode*\n\nExamples:\n• 'Mujhe ek story likhni hai'\n• 'Essay on pollution'\n• 'Ek poem sunao'\n• 'Mujhe motivation chahiye'\n\nBatao kya likhna hai?",
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
    # Remove bot name mention
    text = re.sub(rf'\b{BOT_NAME}\b', '', text, flags=re.IGNORECASE)
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
    user_id = message.get('from', {}).get('id')
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
                        f"👋 Namaste {user_name}! Main {BOT_NAME} hoon with Gemini AI!\n\nNeeche buttons se choose karo! 🔽",
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
                    f"👋 Haan {user_name}! Main {BOT_NAME} yahan hoon.\n\nNeeche buttons use karo ya sawaal likho! 🔽",
                    reply_markup=get_main_keyboard())
        return
    
    # Show typing indicator
    send_typing(chat_id)
    
    # Get AI response from Gemini
    response = get_gemini_response(cleaned, user_name)
    
    # Format response for groups
    if chat_type != 'private' and username:
        response = f"🤖 @{username}\n{response}"
    elif chat_type != 'private':
        response = f"🤖 {user_name}\n{response}"
    
    # Send response with back button
    send_message(chat_id, response, reply_markup=get_back_button())
    
    # Log
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {user_name}: {cleaned[:50]}...")
    print(f"Response: {response[:100]}...")

# ========== SET WEBHOOK ==========
def set_webhook():
    render_url = os.environ.get("RENDER_URL", "")
    if not render_url:
        print("⚠️ RENDER_URL not set, using polling mode...")
        return False
    
    webhook_url = f"{render_url}/webhook"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    
    # Delete old webhook first
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    time.sleep(1)
    
    # Set new webhook
    try:
        response = requests.post(api_url, json={'url': webhook_url})
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ Webhook set: {webhook_url}")
                return True
    except Exception as e:
        print(f"Webhook error: {e}")
    
    return False

# ========== POLLING MODE (Fallback) ==========
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
    print(f"🤖 {BOT_NAME} BOT with Google Gemini AI")
    print("=" * 60)
    
    # Check configuration
    if TELEGRAM_TOKEN == "YAHAN_APNA_TOKEN_DALO":
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        print("✅ Set environment variable: TELEGRAM_TOKEN")
        return
    
    if GEMINI_API_KEY == "YAHAN_APNI_GEMINI_KEY_DALO":
        print("❌ ERROR: GEMINI_API_KEY not set!")
        print("✅ Get your free API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Get bot info
    if not get_bot_info():
        print("❌ Failed to connect to Telegram!")
        return
    
    # Start Flask server
    Thread(target=run_flask, daemon=True).start()
    print(f"✅ Flask server started on port {os.environ.get('PORT', 8080)}")
    
    # Try webhook or fallback to polling
    if not set_webhook():
        print("⚠️ Webhook failed, using polling mode...")
        polling_mode()
    else:
        print("✅ Bot is running with webhook!")
        print("=" * 60)
        print(f"🎯 {BOT_NAME} BOT is LIVE!")
        print(f"🧠 AI Model: Google Gemini 1.5 Flash")
        print("💬 Test: Send /start in private chat")
        print("🔧 Features: AI Chat, Calculator, Coding Help, Translation")
        print("=" * 60)
        
        # Keep main thread alive
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
