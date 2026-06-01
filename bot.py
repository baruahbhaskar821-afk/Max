#!/usr/bin/env python3
"""
MAX BOT - FULL AI BOT with Google Gemini
Jo bhi poocho, sahi jawab dega!
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

# ========== GEMINI AI - JO BHI POCHO JAWAB DEGA ==========
def get_gemini_response(user_message, user_name):
    """Gemini API - Real AI, har sawaal ka jawab"""
    
    # Agar API key nahi hai toh fallback
    if not GEMINI_API_KEY or GEMINI_API_KEY == "":
        return "⚠️ Gemini API key nahi mili! Please add GEMINI_API_KEY environment variable."
    
    # Gemini API URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Smart system prompt
    prompt = f"""Tu {BOT_NAME} hai, ek friendly aur helpful AI assistant. User ka naam {user_name} hai.

Important Rules:
1. Hinglish mein jawab de (Hindi + English mix)
2. Short aur simple rakhe (max 2-3 lines)
3. Jo bhi sawaal poochhe, uska sahi jawab de
4. Agar calculation ho toh calculate kar
5. Friendly ban, emojis use kar
6. Agar kuch nahi pata toh seedha "Mujhe nahi pata" bol de

User ka sawaal: {user_message}

Tera jawab:"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
            "topP": 0.9
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                reply = data['candidates'][0]['content']['parts'][0]['text']
                return reply.strip()
            else:
                return "⚠️ Kuch gadbad ho gayi. Dobara poocho!"
        else:
            print(f"Gemini API Error: {response.status_code}")
            # Try fallback for common questions
            return get_fallback_response(user_message, user_name)
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return get_fallback_response(user_message, user_name)

# ========== FALLBACK (Jab Gemini kaam na kare) ==========
def get_fallback_response(user_message, user_name):
    """Basic fallback - sirf emergency ke liye"""
    
    msg = user_message.lower().strip()
    
    # Calculations
    if '+' in msg or '-' in msg or '*' in msg or '/' in msg:
        try:
            # Simple calculation
            if '+' in msg:
                parts = msg.split('+')
                result = int(parts[0]) + int(parts[1])
                return f"🧮 {parts[0]} + {parts[1]} = {result}"
            elif '-' in msg:
                parts = msg.split('-')
                result = int(parts[0]) - int(parts[1])
                return f"🧮 {parts[0]} - {parts[1]} = {result}"
            elif '*' in msg:
                parts = msg.split('*')
                result = int(parts[0]) * int(parts[1])
                return f"🧮 {parts[0]} × {parts[1]} = {result}"
        except:
            pass
    
    # Time
    if 'time' in msg:
        return f"⏰ Time: {datetime.now().strftime('%I:%M %p')}"
    
    # Greeting
    if msg in ['hi', 'hello', 'namaste']:
        return f"Namaste {user_name}! 👋 Main {BOT_NAME} AI hoon. Koi sawaal poocho!"
    
    # Default
    return f"⚠️ Gemini API key set nahi hai! Please add GEMINI_API_KEY. Tab main har sawaal ka jawab dunga! 🤖"

# ========== KEYBOARDS ==========
def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🤖 AI Chat", "callback_data": "menu_ai"}],
            [{"text": "📚 Help", "callback_data": "menu_help"}],
            [{"text": "ℹ️ About", "callback_data": "menu_about"}],
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
                    f"🤖 *{BOT_NAME} - Main Menu*\n\nKya karna chahte ho?",
                    reply_markup=get_main_keyboard())
    
    elif data == 'menu_help':
        edit_message(chat_id, message_id,
                    f"📚 *Help - Full AI Bot*\n\nKuch bhi poocho!\n\n✅ Examples:\n• 2+2 kya hai?\n• Python kya hai?\n• Saal mein kitne din?\n• Ek joke sunao\n• Good morning ka hindi\n• Time kya hai?\n\nBas sawaal likho!",
                    reply_markup=get_back_button())
    
    elif data == 'menu_about':
        edit_message(chat_id, message_id,
                    f"ℹ️ *About {BOT_NAME}*\n\n🤖 Full AI Assistant\n🧠 Google Gemini AI\n✅ Har sawaal ka jawab\n🆓 Free Forever\n💬 Hinglish",
                    reply_markup=get_back_button())
    
    elif data == 'menu_stats':
        ai_status = "🟢 Gemini Active" if GEMINI_API_KEY else "🔴 API Key Missing"
        edit_message(chat_id, message_id,
                    f"📊 *Status*\n\n✅ Bot: Active\n🧠 AI: {ai_status}\n⏰ Uptime: 24/7\n📝 Response: Real-time",
                    reply_markup=get_back_button())
    
    elif data == 'menu_ai':
        edit_message(chat_id, message_id,
                    "🤖 *AI Chat Mode*\n\nKuch bhi poocho! Main jawab dunga.\n\n✨ Try karo:\n• 2+2 kya hai?\n• Python kya hai?\n• Ek joke sunao\n• Good morning ka hindi\n• Time kya hai?\n\nJo man mein aaye poocho! 🎯",
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
    # Remove bot name
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
                        f"👋 Namaste {user_name}! Main {BOT_NAME} hoon - FULL AI BOT!\n\nKuch bhi poocho! 🎯\n\n✅ Maths\n✅ GK\n✅ Coding\n✅ Jokes\n✅ Translation\n\nKoi bhi sawaal likho!",
                        reply_markup=get_main_keyboard())
            return
        elif cmd == '/help':
            send_message(chat_id,
                        f"📚 *Full AI Help*\n\nKuch bhi poocho!\n\n• 2+2\n• Python kya hai\n• Saal mein kitne din\n• Joke sunao\n• Good morning ka hindi\n\nJo man mein aaye! 🚀",
                        reply_markup=get_back_button())
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
                    f"👋 Haan {user_name}! Main yahan hoon. Koi sawaal likho! 🎯",
                    reply_markup=get_main_keyboard())
        return
    
    # Show typing
    send_typing(chat_id)
    
    # Get AI response from Gemini (jo bhi poocho jawab dega)
    response = get_gemini_response(cleaned, user_name)
    
    # Format response for group
    if chat_type != 'private':
        response = f"🤖 *Reply for {user_name}*\n\n{response}"
    
    # Send response
    send_message(chat_id, response, reply_markup=get_back_button())
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {user_name}: {cleaned[:50]}...")
    print(f"Response sent ✅")

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
    print(f"🤖 {BOT_NAME} BOT - FULL AI VERSION")
    print("=" * 60)
    
    if TELEGRAM_TOKEN == "YAHAN_APNA_TOKEN_DALO":
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        return
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "":
        print("⚠️ WARNING: GEMINI_API_KEY not set!")
        print("✅ Bot will show error message until API key is added")
    
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
        print("🧠 AI Model: Google Gemini 1.5 Flash")
        print("💬 Jo bhi poocho, jawab dega!")
        print("=" * 60)
        print("📝 Test Questions:")
        print("   • 2+2 kya hai?")
        print("   • Python kya hai?")
        print("   • Saal mein kitne din?")
        print("   • Ek joke sunao")
        print("   • Good morning ka hindi")
        print("=" * 60)
        
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
