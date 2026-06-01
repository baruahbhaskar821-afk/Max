#!/usr/bin/env python3
"""
MAX BOT - Full AI Bot with Direct Gemini API Calls
No external AI libraries needed - Works 100% on Render!
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

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YAHAN_APNA_TOKEN_DALO")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
BOT_NAME = "Max"

# ========== FLASK APP ==========
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🤖 Max Bot with Full AI is Running! ✅"

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

# ========== DIRECT GEMINI API CALL (No Library!) ==========
def get_gemini_response(user_message, user_name):
    """Direct API call to Gemini - works without any library!"""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "":
        return get_smart_fallback(user_message, user_name)
    
    # Gemini API URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Smart prompt in Hinglish
    prompt = f"""Tu {BOT_NAME} hai, ek friendly aur smart assistant. User ka naam {user_name} hai.

Rules:
1. Hinglish mein jawab de (Hindi + English mix)
2. Short aur simple rakhe (max 2-3 lines)
3. Agar calculation ho toh calculate kar
4. Friendly ban, emojis use kar
5. Agar nahi pata toh "Mujhe nahi pata" bol de

User question: {user_message}

Answer:"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 250,
            "topP": 0.9
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract text from response
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            else:
                return "⚠️ Kuch gadbad ho gayi. Dobara poocho!"
        else:
            print(f"Gemini API Error: {response.status_code}")
            return get_smart_fallback(user_message, user_name)
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return get_smart_fallback(user_message, user_name)

# ========== SMART FALLBACK (Jab Gemini unavailable ho) ==========
def get_smart_fallback(user_message, user_name):
    """Intelligent fallback - works even without API"""
    
    msg = user_message.lower().strip()
    
    # 1. Calculations
    calc_result = calculate_math(msg)
    if calc_result:
        return f"🧮 {calc_result}"
    
    # 2. Greetings
    if any(g in msg for g in ['hi', 'hello', 'hey', 'namaste', 'hola']):
        return f"Namaste {user_name}! 👋 Kaise ho? Main {BOT_NAME} AI hoon!"
    
    if 'how are you' in msg:
        return f"Main theek hoon {user_name}! 😊 Aap batao? Kya help chahiye?"
    
    # 3. Thanks
    if any(t in msg for t in ['thanks', 'thank you', 'dhanyavad', 'shukriya']):
        return f"Welcome {user_name}! 😊 Main hoon yahan help karne ke liye!"
    
    # 4. About bot
    if 'who are you' in msg or 'kaun ho' in msg:
        return f"""Main {BOT_NAME} hoon! 🤖

✅ Full AI assistant
✅ Calculation kar sakta hoon
✅ Coding mein help
✅ GK answer
✅ Translation

Kuch bhi poocho!"""
    
    # 5. Features
    if 'what can you do' in msg or 'kya kar sakte ho' in msg:
        return f"""Main ye sab kar sakta hoon {user_name}:

🧮 Calculator - 2+2, 10*5
💻 Coding - Python, JavaScript
📚 GK - History, Science
🌐 Translation - Any language
✍️ Writing - Stories, essays
😂 Jokes - Funny jokes

Try karo: "2+2 kya hai?" 🎯"""
    
    # 6. Time & Date
    if 'time' in msg:
        return f"⏰ Current time: {datetime.now().strftime('%I:%M %p')}"
    if 'date' in msg:
        return f"📅 Today: {datetime.now().strftime('%d %B %Y')}"
    
    # 7. Jokes
    if 'joke' in msg or 'hasao' in msg:
        jokes = [
            f"Santa: Banta, teri shadi kab ho rahi?\nBanta: Jab mujhe ladki pasand aa jaye!\nSanta: Tujhe to har ladki pasand aati hai!\nBanta: Isliye shadi nahi ho rahi! 😂",
            f"Teacher: 2+2 kya hota hai?\nSanta: 5!\nTeacher: Nahi, 4 hota hai!\nSanta: Aapke hisaab se 4, mere hisaab se 5! 🧮",
            f"Doctor: Aapko problem kya hai?\nPatient: Mujhe bhoolne ki bimari hai!\nDoctor: Kab se?\nPatient: Kya kab se? 😜"
        ]
        return random.choice(jokes)
    
    # 8. GK
    gk_pairs = {
        'taj mahal': 'Taj Mahal Agra mein hai. Shah Jahan ne apni wife Mumtaz ke liye banwaya tha! 🕌',
        'capital of india': 'India ki capital New Delhi hai! 🇮🇳',
        'pm of india': 'India ke Prime Minister Narendra Modi ji hain! 🇮🇳',
        'python': 'Python ek powerful programming language hai. Easy to learn! 🐍',
        'ai': 'AI (Artificial Intelligence) means machines jo human ki tarah soch sakti hain! 🤖'
    }
    
    for key, answer in gk_pairs.items():
        if key in msg:
            return answer
    
    # 9. Good morning/night
    if 'good morning' in msg:
        return f"Good morning {user_name}! ☀️ Din ki shuruaat mast karo!"
    if 'good night' in msg:
        return f"Good night {user_name}! 🌙 Sweet dreams!"
    
    # 10. Help
    if 'help' in msg:
        return f"""Kya help chahiye {user_name}? 🤔

🔹 Calculation: "2+2"
🔹 GK: "Taj Mahal"
🔹 Coding: "Python kya hai"
🔹 Joke: "Joke sunao"
🔹 Time: "Time kya hai"

Ya /help command use karo! 📚"""
    
    # 11. Default fallback
    fallbacks = [
        f"Main samjha nahi {user_name} 🤔 Kuch aur poocho? Jaise '2+2' ya 'Joke sunao'",
        f"Kya kehna chahte ho {user_name}? 🧮 Calculation likho ya sawaal poocho!",
        f"Thoda clear karo {user_name}! Example: '2+2', 'Python kya hai', ya 'Joke' 💡"
    ]
    return random.choice(fallbacks)

def calculate_math(text):
    """Safe math calculation"""
    # Basic operations
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
                    return f"{a} {match.group(0)[len(str(a))]} {b} = {result:.2f}"
                else:
                    return f"{a} {match.group(0)[len(str(a))]} {b} = {int(result)}"
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
        help_text = f"""
🤖 *{BOT_NAME} - Full AI Bot Help*

*Commands:*
/start - Start bot
/help - Yeh menu

*Examples:*
• "2+2 kya hai?"
• "Python kya hai?"
• "Taj Mahal kisne banaya?"
• "Ek joke sunao"
• "Good morning ka hindi"
• "Time kya hai?"

*Group mein:*
"{BOT_NAME} sawaal" likho

*AI Features:*
✅ Smart Chat | ✅ Calculator | ✅ GK | ✅ Coding Help | ✅ Translation
"""
        edit_message(chat_id, message_id, help_text, reply_markup=get_back_button())
    
    elif data == 'menu_about':
        about_text = f"""
📖 *About {BOT_NAME}*

🤖 *Name:* {BOT_NAME}
🧠 *AI:* Google Gemini + Smart Fallback
💬 *Language:* Hinglish
🆓 *Price:* Free Forever

*Status:* 🟢 Active
*Type:* Full AI Assistant
"""
        edit_message(chat_id, message_id, about_text, reply_markup=get_back_button())
    
    elif data == 'menu_stats':
        ai_status = "🟢 Gemini Active" if GEMINI_API_KEY else "🟡 Smart Fallback"
        stats_text = f"""
📊 *Bot Stats*

✅ Status: Active
🤖 Bot: {BOT_NAME}
🧠 AI Mode: {ai_status}

*Working:* 24/7
*Messages:* Unlimited
*Users:* Global

*Features:* ✅ All Working
"""
        edit_message(chat_id, message_id, stats_text, reply_markup=get_back_button())
    
    elif data == 'menu_features':
        features_text = """
🔧 *Features*

1️⃣ 🧮 Calculator - 2+2, 10*5
2️⃣ 💻 Coding Help - Python, JS
3️⃣ 📚 GK - Taj Mahal, History
4️⃣ 🌐 Translation - Any language
5️⃣ ✍️ Writing - Stories, Essays
6️⃣ 😂 Jokes - Funny jokes

*Try now!* Kuch bhi poocho! 🚀
"""
        edit_message(chat_id, message_id, features_text, reply_markup=get_back_button())
    
    elif data == 'menu_ai':
        edit_message(chat_id, message_id,
                    "🤖 *AI Chat Mode*\n\nBas apna sawaal likho! Main jawab dunga.\n\n✨ Examples:\n• 2+2 kya hai?\n• Python kya hai?\n• Ek joke sunao\n• Good morning ka hindi\n\nKuch bhi poocho!",
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
                        f"👋 Namaste {user_name}! Main {BOT_NAME} hoon - Full AI Bot!\n\nNeeche buttons use karo! 🔽\nYa direct sawaal likho!",
                        reply_markup=get_main_keyboard())
            return
        elif cmd == '/help':
            help_text = f"🤖 *{BOT_NAME} Help*\n\nExamples:\n• 2+2\n• Python kya hai\n• Joke sunao\n• Time kya hai\n\nGroup mein: '{BOT_NAME} sawaal'"
            send_message(chat_id, help_text, reply_markup=get_back_button())
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
    response = get_gemini_response(cleaned, user_name)
    
    # Format for group
    if chat_type != 'private' and username:
        response = f"🤖 @{username}\n{response}"
    elif chat_type != 'private':
        response = f"🤖 {user_name}\n{response}"
    
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
    print(f"🤖 {BOT_NAME} BOT - Full AI Version")
    print("=" * 60)
    
    if TELEGRAM_TOKEN == "YAHAN_APNA_TOKEN_DALO":
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        print("✅ Add environment variable: TELEGRAM_TOKEN")
        return
    
    if not get_bot_info():
        print("❌ Failed to connect to Telegram!")
        return
    
    # Start Flask
    Thread(target=run_flask, daemon=True).start()
    print(f"✅ Flask server started on port {os.environ.get('PORT', 8080)}")
    
    # Start bot
    if not set_webhook():
        print("⚠️ Webhook failed, using polling mode...")
        polling_mode()
    else:
        print("✅ Bot is running with webhook!")
        print("=" * 60)
        print(f"🎯 {BOT_NAME} is LIVE!")
        if GEMINI_API_KEY:
            print("🧠 AI Mode: Google Gemini (Full AI)")
        else:
            print("🧠 AI Mode: Smart Fallback (No API Key)")
        print("💬 Send /start in Telegram")
        print("=" * 60)
        
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
