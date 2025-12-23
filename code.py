import json
import time
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = '8586025437:AAEgKY4lzH6cpxlN92mzBrn7B-93BZLGOxI'
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

def load_promos():
    try:
        with open('promos.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_promos(promos):
    with open('promos.json', 'w') as f:
        json.dump(promos, f, indent=4)

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
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Подарок", callback_data='gift')],
        [InlineKeyboardButton("Бонус", callback_data='bonus')],
        [InlineKeyboardButton("Магазин Гемов", callback_data='shop')],
        [InlineKeyboardButton("Магазин Драв Коин", callback_data='drawshop')],
        [InlineKeyboardButton("Промокод", callback_data='promo_button')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('GIFT DRAW BOT\n\nМеню:', reply_markup=reply_markup)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    
    menu_text = """Доступные команды:

/start - Главное меню
/balance - Показать баланс
/gift - Получить ежедневный подарок
/bonus - Получить ежедневный бонус
/shop - Магазин Гемов
/drawshop - Магазин Драв Коин
/promo [код] - Активировать промокод
/menu - Показать это меню"""
    
    await update.message.reply_text(menu_text)

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

async def drawshop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    keyboard = [
        [InlineKeyboardButton("2500", callback_data='drawshop_2500'),
         InlineKeyboardButton("5000", callback_data='drawshop_5000')],
        [InlineKeyboardButton("10000", callback_data='drawshop_10000'),
         InlineKeyboardButton("50000", callback_data='drawshop_50000')],
        [InlineKeyboardButton("???", callback_data='drawshop_100')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Магазин🏪:\n\n2500 Гемов в ттд - 1 Драв коин\n5000 Гемов в ттд - 3 Драв коина\n10000 гемов в ттд - 10 Драв коинов\n50000 Гемов в ттд - 30 Драв коинов\n??? - 100 Драв коинов"
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

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    
    args = context.args
    user_id = update.effective_user.id
    
    if len(args) == 0:
        await update.message.reply_text("Введите код промокода после команды /promo")
        return
    
    promo_code = args[0].upper()
    promos = load_promos()
    
    if promo_code not in promos:
        await update.message.reply_text("❌️ Промокода не существует")
        return
    
    promo_data = promos[promo_code]
    data = load_data()
    user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0})
    
    if promo_data['currency'] == 'gems':
        user_data['gems'] += promo_data['prize']
        reward = f"{promo_data['prize']} Gems💎"
    else:
        user_data['draw_coins'] += promo_data['prize']
        reward = f"{promo_data['prize']} Draw Coin✏️"
    
    save_data(data)
    
    promo_data['activations'] += 1
    if promo_data['max_activations'] > 0 and promo_data['activations'] >= promo_data['max_activations']:
        del promos[promo_code]
    save_promos(promos)
    
    await update.message.reply_text(f"✅️ Получено {reward}\n\n/balance")

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text("Используйте бота в личных сообщениях!")
        return
    
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("Команда только для администраторов")
        return
    
    context.user_data['create_promo'] = {
        'name': 'Не установлено',
        'currency': 'Не установлено',
        'prize': 0,
        'max_activations': 0
    }
    
    keyboard = [
        [InlineKeyboardButton("Название: Не установлено", callback_data='create_name')],
        [InlineKeyboardButton("Валюта: Не установлено", callback_data='create_currency')],
        [InlineKeyboardButton("Награда: 0", callback_data='create_prize')],
        [InlineKeyboardButton("Активации: 0", callback_data='create_activations')],
        [InlineKeyboardButton("Создать промокод", callback_data='create_final')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅️ Создание промокода:", reply_markup=reply_markup)

async def handle_create_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        return
    
    if 'create_promo' not in context.user_data:
        return
    
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return
    
    if 'awaiting_create_input' not in context.user_data:
        return
    
    field = context.user_data['awaiting_create_input']
    text = update.message.text.strip()
    
    try:
        if field == 'name':
            if len(text) < 1:
                await update.message.reply_text("Название должно быть не менее 1 символа")
                return
            context.user_data['create_promo']['name'] = text.upper()
        elif field == 'prize':
            prize = int(text)
            if prize <= 0:
                await update.message.reply_text("Награда должна быть положительным числом")
                return
            context.user_data['create_promo']['prize'] = prize
        elif field == 'activations':
            activations = int(text)
            if activations < 0:
                await update.message.reply_text("Количество активаций должно быть неотрицательным числом")
                return
            context.user_data['create_promo']['max_activations'] = activations
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число")
        return
    
    del context.user_data['awaiting_create_input']
    
    keyboard = [
        [InlineKeyboardButton(f"Название: {context.user_data['create_promo']['name']}", callback_data='create_name')],
        [InlineKeyboardButton(f"Валюта: {context.user_data['create_promo']['currency']}", callback_data='create_currency')],
        [InlineKeyboardButton(f"Награда: {context.user_data['create_promo']['prize']}", callback_data='create_prize')],
        [InlineKeyboardButton(f"Активации: {context.user_data['create_promo']['max_activations']}", callback_data='create_activations')],
        [InlineKeyboardButton("Создать промокод", callback_data='create_final')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅️ Создание промокода:", reply_markup=reply_markup)

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
    
    elif query.data == 'drawshop':
        keyboard = [
            [InlineKeyboardButton("2500", callback_data='drawshop_2500'),
             InlineKeyboardButton("5000", callback_data='drawshop_5000')],
            [InlineKeyboardButton("10000", callback_data='drawshop_10000'),
             InlineKeyboardButton("50000", callback_data='drawshop_50000')],
            [InlineKeyboardButton("???", callback_data='drawshop_100')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Магазин🏪:\n\n2500 Гемов в ттд - 1 Драв коин\n5000 Гемов в ттд - 3 Драв коина\n10000 гемов в ттд - 10 Драв коинов\n50000 Гемов в ттд - 30 Драв коинов\n??? - 100 Драв коинов"
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif query.data == 'promo_button':
        await query.edit_message_text(text="Введите команду /promo [код] для активации промокода")
    
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
    
    elif query.data.startswith('drawshop_'):
        data = load_data()
        user_data = data.setdefault(str(user_id), {'gems': 0, 'draw_coins': 0})
        
        prices = {'drawshop_2500': 1, 'drawshop_5000': 3, 'drawshop_10000': 10, 'drawshop_50000': 30, 'drawshop_100': 100}
        price = prices.get(query.data, 0)
        
        if user_data['draw_coins'] >= price:
            context.user_data['drawshop_item'] = query.data
            context.user_data['drawshop_price'] = price
            await query.edit_message_text(text="Введи ник чтобы получить гемы:")
        else:
            await query.edit_message_text(text="Недостаточно Draw Coin!")
    
    elif query.data.startswith('create_'):
        if user_id not in ADMINS:
            return
        
        if query.data == 'create_name':
            context.user_data['awaiting_create_input'] = 'name'
            await query.edit_message_text(text="Введите название промокода:")
        
        elif query.data == 'create_currency':
            keyboard = [
                [InlineKeyboardButton("Гемы", callback_data='currency_gems'),
                 InlineKeyboardButton("DrawCoin", callback_data='currency_drawcoin')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Выберите валюту награды:", reply_markup=reply_markup)
        
        elif query.data == 'create_prize':
            context.user_data['awaiting_create_input'] = 'prize'
            await query.edit_message_text(text="Введите количество награды:")
        
        elif query.data == 'create_activations':
            context.user_data['awaiting_create_input'] = 'activations'
            await query.edit_message_text(text="Введите максимальное количество активаций (0 - без ограничений):")
        
        elif query.data == 'create_final':
            promo_data = context.user_data.get('create_promo')
            if not promo_data:
                return
            
            if promo_data['name'] == 'Не установлено':
                await query.edit_message_text(text="Пожалуйста, установите название промокода")
                return
            
            if promo_data['currency'] == 'Не установлено':
                await query.edit_message_text(text="Пожалуйста, установите валюту награды")
                return
            
            if promo_data['prize'] <= 0:
                await query.edit_message_text(text="Награда должна быть положительным числом")
                return
            
            promos = load_promos()
            promo_code = promo_data['name']
            
            promos[promo_code] = {
                'currency': promo_data['currency'],
                'prize': promo_data['prize'],
                'max_activations': promo_data['max_activations'],
                'activations': 0
            }
            save_promos(promos)
            
            del context.user_data['create_promo']
            if 'awaiting_create_input' in context.user_data:
                del context.user_data['awaiting_create_input']
            
            await query.edit_message_text(text=f"✅️ Промокод {promo_code} создан!")
    
    elif query.data.startswith('currency_'):
        if user_id not in ADMINS:
            return
        
        if query.data == 'currency_gems':
            context.user_data['create_promo']['currency'] = 'gems'
        else:
            context.user_data['create_promo']['currency'] = 'draw_coins'
        
        keyboard = [
            [InlineKeyboardButton(f"Название: {context.user_data['create_promo']['name']}", callback_data='create_name')],
            [InlineKeyboardButton(f"Валюта: {context.user_data['create_promo']['currency']}", callback_data='create_currency')],
            [InlineKeyboardButton(f"Награда: {context.user_data['create_promo']['prize']}", callback_data='create_prize')],
            [InlineKeyboardButton(f"Активации: {context.user_data['create_promo']['max_activations']}", callback_data='create_activations')],
            [InlineKeyboardButton("Создать промокод", callback_data='create_final')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="✅️ Создание промокода:", reply_markup=reply_markup)

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
        return
    
    if 'drawshop_item' in context.user_data:
        drawshop_item = context.user_data['drawshop_item']
        price = context.user_data['drawshop_price']
        username = update.message.text.strip()
        user_id = update.effective_user.id
        
        data = load_data()
        user_data = data.get(str(user_id), {'gems': 0, 'draw_coins': 0})
        
        gems_bought = 0
        if drawshop_item == 'drawshop_2500': gems_bought = 2500
        elif drawshop_item == 'drawshop_5000': gems_bought = 5000
        elif drawshop_item == 'drawshop_10000': gems_bought = 10000
        elif drawshop_item == 'drawshop_50000': gems_bought = 50000
        elif drawshop_item == 'drawshop_100': gems_bought = 100000
        
        if user_data['draw_coins'] >= price:
            user_data['draw_coins'] -= price
            save_data(data)
            
            for admin in ADMINS:
                await context.bot.send_message(admin, f"[{user_id}] (@{update.effective_user.username}) выводит {gems_bought} гемов за {price} Draw Coin\n\nНик: {username}")
            
            await update.message.reply_text("Запрос на вывод отправлен администраторам")
        else:
            await update.message.reply_text("Недостаточно Draw Coin!")
        
        context.user_data.pop('drawshop_item', None)
        context.user_data.pop('drawshop_price', None)
        return
    
    if 'awaiting_create_input' in context.user_data:
        await handle_create_message(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('gift', gift))
    application.add_handler(CommandHandler('bonus', bonus))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('drawshop', drawshop))
    application.add_handler(CommandHandler('update', update_command))
    application.add_handler(CommandHandler('promo', promo))
    application.add_handler(CommandHandler('create', create))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    print('бот запущен')
    main()
