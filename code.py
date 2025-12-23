print('Бот запущен.')
import json
import time
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = '8430405776:AAEDlQ51BMGeY7VQVTTA0tzuaznURyY9uv0'
ADMINS = [7988581841, 8449326470]

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_version():
    try:
        with open('v.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_version(version):
    with open('v.txt', 'w') as f:
        f.write(str(version))

def get_random_gift():
    rand = random.random() * 100
    if rand < 60: return 1000
    if rand < 85: return 2500
    if rand < 99.9: return 5000
    return 10000

def get_random_bonus():
    rand = random.random() * 100
    if rand < 80: return 500
    if rand < 99: return 1000
    return 3000

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    keyboard = [
        [InlineKeyboardButton("Баланс", callback_data='balance'),
         InlineKeyboardButton("Подарок", callback_data='gift')],
        [InlineKeyboardButton("Бонус", callback_data='bonus'),
         InlineKeyboardButton("Магазин", callback_data='shop')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('GIFT DRAW BOT\n\nМеню:', reply_markup=reply_markup)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    user_id = update.effective_user.id
    data = load_data()
    user_data = data.get(str(user_id), {'gems': 0, 'draw_coins': 0})
    text = f"Баланс:\n\n{user_data['gems']} Gems💎\n{user_data['draw_coins']} Draw Coin✏️"
    await update.message.reply_text(text)

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    user_id = update.effective_user.id
    data = load_data()
    user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0, 'last_gift': 0})
    
    current_time = time.time()
    last_gift = user_data.get('last_gift', 0)
    
    if current_time - last_gift < 86400:
        remaining = 86400 - (current_time - last_gift)
        await update.message.reply_text(f"Вы уже получали сегодня подарок!\nВернитесь через {format_time(remaining)} секунд")
        return
    
    amount = get_random_gift()
    user_data['gems'] += amount
    user_data['last_gift'] = current_time
    save_data(data)
    
    keyboard = [[InlineKeyboardButton("Посмотреть баланс", callback_data='balance')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Вы получили {amount} гемов\nНапишите /balance для просмотра баланса", reply_markup=reply_markup)

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    user_id = update.effective_user.id
    data = load_data()
    user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0, 'last_bonus': 0})
    
    current_time = time.time()
    last_bonus = user_data.get('last_bonus', 0)
    
    if current_time - last_bonus < 86400:
        remaining = 86400 - (current_time - last_bonus)
        await update.message.reply_text(f"Вы уже получали сегодня бонус!\nВернитесь через {format_time(remaining)} секунд")
        return
    
    amount = get_random_bonus()
    user_data['gems'] += amount
    user_data['last_bonus'] = current_time
    save_data(data)
    
    keyboard = [[InlineKeyboardButton("Посмотреть баланс", callback_data='balance')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Вы получили {amount} гемов\nНапишите /balance для просмотра баланса", reply_markup=reply_markup)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    keyboard = [
        [InlineKeyboardButton("1000", callback_data='shop_1000'),
         InlineKeyboardButton("3000", callback_data='shop_3000')],
        [InlineKeyboardButton("5000", callback_data='shop_5000'),
         InlineKeyboardButton("10000", callback_data='shop_10000')],
        [InlineKeyboardButton("???", callback_data='shop_99999')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Магазин🏪:\n\n1000 Гемов в ттд - 2000 гемов бота\n3000 гемов в ттд - 6000 гемов бота\n5000 гемов в ттд - 11000 гемов бота\n10000 гемов в ттд - 20000 гемов бота\n??? - 99999 гемов бота"
    await update.message.reply_text(text, reply_markup=reply_markup)

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("Команда только для администраторов")
        return
    
    try:
        response = requests.get('https://raw.githubusercontent.com/rqcbjnyfqruibuwk/focsoeeijzambquc/refs/heads/main/version.txt')
        remote_version = int(response.text.strip())
    except:
        await update.message.reply_text("Ошибка при проверке версии")
        return
    
    local_version = load_version()
    
    if remote_version > local_version:
        try:
            response = requests.get('https://raw.githubusercontent.com/rqcbjnyfqruibuwk/focsoeeijzambquc/refs/heads/main/code.py')
            new_code = response.text
            with open(__file__, 'w') as f:
                f.write(new_code)
            save_version(remote_version)
            await update.message.reply_text(f"Обновлено до v{remote_version}")
            import subprocess
            subprocess.run(["python3", __file__])
            exit(0)
        except:
            await update.message.reply_text("Ошибка при обновлении")
    else:
        await update.message.reply_text(f"Текущая версия v{local_version} актуальна")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == 'balance':
        data = load_data()
        user_data = data.get(str(user_id), {'gems': 0, 'draw_coins': 0})
        text = f"Баланс:\n\n{user_data['gems']} Gems💎\n{user_data['draw_coins']} Draw Coin✏️"
        await query.edit_message_text(text=text)
    
    elif query.data == 'gift':
        data = load_data()
        user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0, 'last_gift': 0})
        
        current_time = time.time()
        last_gift = user_data.get('last_gift', 0)
        
        if current_time - last_gift < 86400:
            remaining = 86400 - (current_time - last_gift)
            await query.edit_message_text(text=f"Вы уже получали сегодня подарок!\nВернитесь через {format_time(remaining)} секунд")
            return
        
        amount = get_random_gift()
        user_data['gems'] += amount
        user_data['last_gift'] = current_time
        save_data(data)
        
        keyboard = [[InlineKeyboardButton("Посмотреть баланс", callback_data='balance')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Вы получили {amount} гемов\nНапишите /balance для просмотра баланса", reply_markup=reply_markup)
    
    elif query.data == 'bonus':
        data = load_data()
        user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0, 'last_bonus': 0})
        
        current_time = time.time()
        last_bonus = user_data.get('last_bonus', 0)
        
        if current_time - last_bonus < 86400:
            remaining = 86400 - (current_time - last_bonus)
            await query.edit_message_text(text=f"Вы уже получали сегодня бонус!\nВернитесь через {format_time(remaining)} секунд")
            return
        
        amount = get_random_bonus()
        user_data['gems'] += amount
        user_data['last_bonus'] = current_time
        save_data(data)
        
        keyboard = [[InlineKeyboardButton("Посмотреть баланс", callback_data='balance')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Вы получили {amount} гемов\nНапишите /balance для просмотра баланса", reply_markup=reply_markup)
    
    elif query.data == 'shop':
        keyboard = [
            [InlineKeyboardButton("1000", callback_data='shop_1000'),
             InlineKeyboardButton("3000", callback_data='shop_3000')],
            [InlineKeyboardButton("5000", callback_data='shop_5000'),
             InlineKeyboardButton("10000", callback_data='shop_10000')],
            [InlineKeyboardButton("???", callback_data='shop_99999')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Магазин🏪:\n\n1000 Гемов в ттд - 2000 гемов бота\n3000 гемов в ттд - 6000 гемов бота\n5000 гемов в ттд - 11000 гемов бота\n10000 гемов в ттд - 20000 гемов бота\n??? - 99999 гемов бота"
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif query.data.startswith('shop_'):
        data = load_data()
        user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0})
        
        prices = {'shop_1000': 2000, 'shop_3000': 6000, 'shop_5000': 11000, 'shop_10000': 20000, 'shop_99999': 99999}
        price = prices.get(query.data, 0)
        
        if user_data['gems'] >= price:
            context.user_data['shop_item'] = query.data
            context.user_data['shop_price'] = price
            await query.edit_message_text(text="Введи ник чтобы получить гемы:")
        else:
            await query.edit_message_text(text="Недостаточно гемов!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        return
        
    if 'shop_item' in context.user_data:
        shop_item = context.user_data['shop_item']
        price = context.user_data['shop_price']
        username = update.message.text.strip()
        user_id = update.effective_user.id
        
        data = load_data()
        user_data = data.get(str(user_id), {'gems': 0, 'draw_coins': 0})
        
        gems_bought = 0
        if shop_item == 'shop_1000': gems_bought = 1000
        elif shop_item == 'shop_3000': gems_bought = 3000
        elif shop_item == 'shop_5000': gems_bought = 5000
        elif shop_item == 'shop_10000': gems_bought = 10000
        elif shop_item == 'shop_99999': gems_bought = 99999
        
        if user_data['gems'] >= price:
            user_data['gems'] -= price
            save_data(data)
            
            for admin in ADMINS:
                await context.bot.send_message(admin, f"[{user_id}] (@{update.effective_user.username}) выводит {gems_bought}\n\nНик: {username}")
            
            await update.message.reply_text("Запрос на вывод отправлен администраторам")
        else:
            await update.message.reply_text("Недостаточно гемов!")
        
        context.user_data.pop('shop_item', None)
        context.user_data.pop('shop_price', None)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('gift', gift))
    application.add_handler(CommandHandler('bonus', bonus))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('update', update_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
