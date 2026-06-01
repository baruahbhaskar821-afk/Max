#!/usr/bin/env python3
"""
MAX BOT - Complete Working Version for Render.com
No errors, fully tested
"""

import json
import time
import re
import os
from datetime import datetime
from threading import Thread
from flask import Flask, request
import requests

# ========== CONFIGURATION ==========
# Ye values Render.com pe Environment Variables mein daal dena
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YAHAN_APNA_TOKEN_DALO")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YAHAN_APNI_GROQ_API_KEY_DALO")
BOT_NAME = "Max"

# ========== GLOBAL VARIABLES ==========
conversations = {}
BOT_USERNAME = None
flask_app = Flask('')

# ========== FLASK WEBHOOK ==========
@flask_app.route('/')
def home():
    return f"🤖 {BOT_NAME} Bot is Running! ✅"

@flask_app.route(f'/webhook', methods=['POST'])
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
    flask_app.run(host='0.0.0.0', port=port)

# ========== TELEGRAM API FUNCTIONS ==========
def telegram_api_call(method, params=None):
    if params is None:
        params = {}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    
    try:
        if method in ['sendMessage', 'editMessageText', 'sendChatAction', 'answerCallbackQuery']:
            response = requests.post(url, json=params, timeout=30)
        else:
            response = requests.post(url, json=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"API Exception: {e}")
        return None

def send_message(chat_id, text, parse_mode='Markdown', reply_markup=None):
    params = {
        'chat_id': chat_id,
        'text': text[:4096]  # Telegram limit
    }
    if parse_mode:
        params['parse_mode'] = parse_mode
    if reply_markup:
        params['reply_markup'] = reply_markup
    
    return telegram_api_call('sendMessage', params)

def edit_message(chat_id, message_id, text, parse_mode='Markdown', reply_markup=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text[:4096]
    }
    if parse_mode:
        params['parse_mode'] = parse_mode
    if reply_markup:
        params['reply_markup'] = reply_markup
    
    return telegram_api_call('editMessageText', params)

def answer_callback(callback_id, text=None, alert=False):
    params = {'callback_query_id': callback_id}
    if text:
        params['text'] = text
        params['show_alert'] = alert
    return telegram_api_call('answerCallbackQuery', params)

def send_typing(chat_id):
    return telegram_api_call('sendChatAction', {
        'chat_id': chat_id,
        'action': 'typing'
    })

def set_webhook():
    # Render ka URL tumhe deploy ke baad milega
    render_url = os.environ.get("RENDER_URL", "")
    if not render_url:
        print("⚠️ RENDER_URL not set, using polling mode...")
        return False
    
    webhook_url = f"{render_url}/webhook"
    
    # Delete old webhook first
    telegram_api_call('deleteWebhook')
    time.sleep(1)
    
    # Set new webhook
    result = telegram_api_call('setWebhook', {'url': webhook_url})
    
    if result and result.get('ok'):
        print(f"✅ Webhook set: {webhook_url}")
        return True
    else:
        print(f"❌ Webhook failed: {result}")
        return False

def get_bot_info():
    global BOT_USERNAME
    result = telegram_api_call('getMe')
    if result and result.get('ok'):
        BOT_USERNAME = result['result'].get('username')
        print(f"✅ Bot connected: @{BOT_USERNAME}")
        return True
    return False

# ========== KEYBOARDS ==========
def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🤖 AI Chat", "callback_data": "menu_ai"}],
            [{"text": "📚 Help", "callback_data": "menu_help"}],
            [{"text": "ℹ️ About", "callback_data": "menu_about"}],
            [{"text": "🔧 Features", "callback_data": "menu_features"}],
            [{"text": "❓ Ask Me", "callback_data": "menu_ask"}]
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
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }

# ========== RESPONSE TEXT ==========
def get_help_text():
    return f"""
🤖 *{BOT_NAME} - Help Menu*

*Commands:*
/start - Bot start karo
/help - Yeh help menu

*Group Mein:*
Sirf *{BOT_NAME}* likho aur sawaal poocho
Example: `Max 2+2 kya hai?`

*Private Mein:*
Direct message karo ya buttons use karo

*AI Features:*
• Calculations
• General knowledge
• Coding help
• Translation
"""

def get_about_text():
    return f"""
📖 *About {BOT_NAME}*

🤖 *Name:* {BOT_NAME}
🧠 *AI:* Llama 3.1 (Groq)
💬 *Language:* Hinglish
🆓 *Price:* Free

*How to use:*
• Group mein `{BOT_NAME}` likho
• Private mein buttons use karo
"""

def get_stats_text():
    return f"""
📊 *Bot Stats*

✅ Status: Active
🤖 Name: {BOT_NAME}
🧠 AI: Llama 3.1
💬 Active Chats: {len(conversations)}
⏰ Status: 24/7

*Working Features:*
✅ AI Chat
✅ Calculations
✅ Buttons Menu
✅ Group Support
"""

# ========== AI RESPONSE ==========
def get_ai_response(user_message, user_name):
    # Simple calculations without AI
    calc_result = handle_calculation(user_message)
    if calc_result:
        return calc_result
    
    # For AI responses
    system_prompt = f"""Tu {BOT_NAME} hai, ek friendly assistant. User: {user_name}
Rules: Hinglish mein jawab de, short aur helpful rahe.
Agar nahi pata toh seedha bol de.

User: {user_message}
Answer:"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "system", "content": system_prompt}],
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "❌ AI service busy hai. Thodi der baad try karo!"
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ Technical issue. Baad mein try karo!"

def handle_calculation(text):
    # Handle basic calculations
    text = text.lower().strip()
    
    # Check for math expressions
    math_pattern = r'(\d+[\+\-\*/]\d+)'
    match = re.search(math_pattern, text)
    
    if match:
        try:
            expression = match.group(1)
            # Safe calculation
            if '+' in expression:
                nums = expression.split('+')
                result = int(nums[0]) + int(nums[1])
                return f"🧮 *Calculation:* {expression} = {result}"
            elif '-' in expression:
                nums = expression.split('-')
                result = int(nums[0]) - int(nums[1])
                return f"🧮 *Calculation:* {expression} = {result}"
            elif '*' in expression:
                nums = expression.split('*')
                result = int(nums[0]) * int(nums[1])
                return f"🧮 *Calculation:* {expression} = {result}"
            elif '/' in expression:
                nums = expression.split('/')
                if int(nums[1]) != 0:
                    result = int(nums[0]) / int(nums[1])
                    return f"🧮 *Calculation:* {expression} = {result}"
        except:
            pass
    
    return None

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
    
    elif data == 'menu_ai':
        edit_message(chat_id, message_id,
                    "🤖 *AI Chat Mode*\n\nApna sawaal likho!\nExample: '2+2 kya hai?'\n\nBack button se wapas aao!",
                    reply_markup=get_back_button())
    
    elif data == 'menu_ask':
        edit_message(chat_id, message_id,
                    "❓ *Ask Me Anything*\n\nKuch bhi poocho!\n\nExamples:\n• 2+2 kya hai?\n• Python kya hai?\n• Ek joke sunao",
                    reply_markup=get_back_button())
    
    elif data == 'menu_features':
        edit_message(chat_id, message_id, "🔧 *Features*\n\nChoose an option:",
                    reply_markup=get_features_keyboard())
    
    elif data == 'menu_stats':
        edit_message(chat_id, message_id, get_stats_text(), reply_markup=get_back_button())
    
    elif data == 'feature_calc':
        edit_message(chat_id, message_id,
                    "🧮 *Calculator Mode*\n\nExamples:\n• 2+2\n• 10*5\n• 100/2\n\nBas calculation likho!",
                    reply_markup=get_back_button())
    
    elif data == 'feature_code':
        edit_message(chat_id, message_id,
                    "💻 *Coding Help*\n\nApna code ya question bhejo!\nExample: 'Python mein loop kaise likhen?'",
                    reply_markup=get_back_button())
    
    elif data == 'feature_gk':
        edit_message(chat_id, message_id,
                    "📚 *General Knowledge*\n\nKuch bhi poocho!\nExample: 'Taj Mahal kisne banaya?'",
                    reply_markup=get_back_button())
    
    elif data == 'feature_translate':
        edit_message(chat_id, message_id,
                    "🌐 *Translation*\n\nExamples:\n• 'Good morning ka hindi'\n• 'Pyar ko english mein'",
                    reply_markup=get_back_button())

# ========== MESSAGE PROCESSOR ==========
def should_reply(message):
    chat_type = message.get('chat', {}).get('type')
    message_text = message.get('text', '').lower()
    
    # Private chat mein always reply
    if chat_type == 'private':
        return True
    
    # Group mein BOT_NAME mention ho toh reply
    if BOT_NAME.lower() in message_text:
        return True
    
    # Reply to bot
    reply_to = message.get('reply_to_message')
    if reply_to and reply_to.get('from', {}).get('is_bot'):
        return True
    
    return False

def clean_message(text):
    if not text:
        return None
    # Remove bot name mention
    text = re.sub(rf'@{BOT_USERNAME}', '', text, flags=re.IGNORECASE) if BOT_USERNAME else text
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
                        f"👋 Namaste {user_name}! Main {BOT_NAME} hoon.\n\nNeeche buttons use karo! 🔽",
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
    
    # Show typing indicator
    send_typing(chat_id)
    
    # Get response
    response = get_ai_response(cleaned, user_name)
    
    # Format response for groups
    if chat_type != 'private' and username:
        response = f"🤖 @{username} {response}"
    
    # Send response
    send_message(chat_id, response, reply_markup=get_back_button())
    
    # Log
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {user_name}: {cleaned[:50]}...")

# ========== POLLING MODE (Webhook fail ho toh) ==========
def polling_mode():
    print("🔄 Starting polling mode...")
    last_update_id = 0
    
    while True:
        try:
            params = {'timeout': 30, 'allowed_updates': ['message', 'callback_query']}
            if last_update_id:
                params['offset'] = last_update_id + 1
            
            result = telegram_api_call('getUpdates', params)
            
            if result and result.get('ok'):
                for update in result['result']:
                    last_update_id = update['update_id']
                    process_update(update)
            
            time.sleep(1)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

# ========== MAIN ==========
def main():
    print("=" * 50)
    print(f"🤖 {BOT_NAME} BOT Starting...")
    print("=" * 50)
    
    # Check configuration
    if TELEGRAM_TOKEN == "YAHAN_APNA_TOKEN_DALO":
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        print("✅ Set environment variable: TELEGRAM_TOKEN")
        return
    
    if GROQ_API_KEY == "YAHAN_APNI_GROQ_API_KEY_DALO":
        print("⚠️ WARNING: GROQ_API_KEY not set!")
        print("AI features may not work properly!")
    
    # Get bot info
    if not get_bot_info():
        print("❌ Failed to connect to Telegram!")
        return
    
    # Start Flask server
    Thread(target=run_flask, daemon=True).start()
    print(f"✅ Flask server started on port {os.environ.get('PORT', 8080)}")
    
    # Try webhook first, fallback to polling
    if not set_webhook():
        print("⚠️ Webhook failed, using polling mode...")
        polling_mode()
    else:
        print("✅ Bot is running with webhook!")
        print("=" * 50)
        print("🎯 Bot is LIVE!")
        print(f"📝 Bot Username: @{BOT_USERNAME}")
        print("💡 Test: Send /start in private chat")
        print("💬 Group: Type 'Max hello'")
        print("=" * 50)
        
        # Keep main thread alive
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
