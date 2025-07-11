import telebot
from telebot import types
from PIL import Image  # Для обработки изображений
import os

# Замените на свой токен
BOT_TOKEN = "8177335454:AAExDJLIcmi-2deehgxtrruyBiv90LwlGJE"
GROUP_ID = -1002609493790  # Замените на ID вашей группы


bot = telebot.TeleBot(BOT_TOKEN)

# Глобальные переменные для хранения данных о заказе
current_action = None  # 'hookah' или 'bar'
current_zone = None
current_type = None
current_row = None
current_place = None
current_order = None

def reset_state():
    global current_action, current_zone, current_type, current_row, current_place, current_order
    current_action = None
    current_zone = None
    current_type = None
    current_row = None
    current_place = None
    current_order = None

# --- Клавиатуры ---

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_hookah = types.KeyboardButton("Вызвать кальянного мастера")
    item_bar = types.KeyboardButton("Заказать по меню Бара")
    markup.add(item_hookah, item_bar)
    return markup

def create_zone_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_yellow = types.KeyboardButton("Желтая зона")
    item_green = types.KeyboardButton("Зеленая зона")
    item_back = types.KeyboardButton("Назад")
    markup.add(item_yellow, item_green, item_back)
    return markup

def create_yellow_type_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_lezhak = types.KeyboardButton("Лежак")
    item_shater = types.KeyboardButton("Шатер")
    item_divan = types.KeyboardButton("Диван-кровать")
    item_naves = types.KeyboardButton("Навес")
    item_back = types.KeyboardButton("Назад")
    markup.add(item_lezhak, item_shater, item_divan, item_naves, item_back)
    return markup

def create_lezhak_row_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_row1 = types.KeyboardButton("Ряд 1")
    item_row2 = types.KeyboardButton("Ряд 2")
    item_row3 = types.KeyboardButton("Ряд 3")
    item_back = types.KeyboardButton("Назад")
    markup.add(item_row1, item_row2, item_row3, item_back)
    return markup

def create_green_row_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row_buttons = [types.KeyboardButton(f"Ряд {i}") for i in range(1, 9)]
    markup.add(*row_buttons)  # Добавляем все кнопки рядов
    item_back = types.KeyboardButton("Назад")
    markup.add(item_back)
    return markup

# --- Обработчики ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    global current_action, current_zone, current_type, current_row, current_place, current_order
    # Сбрасываем все переменные состояния
    current_action = None
    current_zone = None
    current_type = None
    current_row = None
    current_place = None
    current_order = None

    with open("menu.png", 'rb') as photo, open("hookha-menu.png", 'rb') as photo2: # Замените на путь к вашему изображению
        bot.send_photo(message.chat.id, photo)
        bot.send_photo(message.chat.id, photo2)
        bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=create_main_menu())

@bot.message_handler(func=lambda message: message.text == "Вызвать кальянного мастера")
def handle_hookah(message):
    global current_action
    current_action = 'hookah'
    bot.send_message(message.chat.id, "Выберите зону:", reply_markup=create_zone_keyboard())

@bot.message_handler(func=lambda message: message.text == "Заказать по меню Бара")
def handle_bar(message):
    global current_action
    current_action = 'bar'
    bot.send_message(message.chat.id, "Напишите, пожалуйста, что Вам принести:")
    bot.register_next_step_handler(message, get_order)

def get_order(message):
    global current_order
    current_order = message.text
    bot.send_message(message.chat.id, "Выберите зону:", reply_markup=create_zone_keyboard())

@bot.message_handler(func=lambda message: message.text in ["Желтая зона", "Зеленая зона"])
def handle_zone(message):
    global current_zone
    current_zone = message.text
    if current_zone == "Желтая зона":
        bot.send_message(message.chat.id, "Выберите тип:", reply_markup=create_yellow_type_keyboard())
    elif current_zone == "Зеленая зона":
        bot.send_message(message.chat.id, "Выберите ряд:", reply_markup=create_green_row_keyboard())

@bot.message_handler(func=lambda message: message.text in ["Лежак", "Шатер", "Диван-кровать", "Навес"])
def handle_yellow_type(message):
    global current_type
    current_type = message.text
    if current_type == "Лежак":
        bot.send_message(message.chat.id, "Выберите ряд:", reply_markup=create_lezhak_row_keyboard())
    else:
        bot.send_message(message.chat.id, "Напишите номер места (только цифры):")
        bot.register_next_step_handler(message, get_place)

@bot.message_handler(func=lambda message: message.text in [f"Ряд {i}" for i in range(1, 9)] + ["Ряд 1", "Ряд 2", "Ряд 3"])
def handle_row(message):
    global current_row
    current_row = message.text
    bot.send_message(message.chat.id, "Напишите номер места (только цифры):")
    bot.register_next_step_handler(message, get_place)

def get_place(message):
    global current_place
    current_place = message.text.strip()

    # Проверка, что пользователь ввел номер места (только цифры)
    if not current_place.isdigit():
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер места (только цифры):")
        bot.register_next_step_handler(message, get_place)
        return
        # Ограничение длины номера места до 2 символов
    if len(current_place) > 2:
        bot.send_message(message.chat.id, "Пожалуйста, введите максимум двузначное число номера места:")
        bot.register_next_step_handler(message, get_place)
        return
    # Проверка наличия всех необходимых данных перед отправкой
    if current_action is None or current_zone is None:
        bot.send_message(message.chat.id, "Похоже, что вы начали новый заказ или произошла ошибка. Пожалуйста, нажмите /start для начала.")
        return

    # Формируем сообщение для группы
    if current_action == 'hookah':
        message_to_group = f"Новый заказ кальяна:\nЗона: {current_zone}\n"
        if current_type:
            message_to_group += f"Тип: {current_type}\n"
        if current_row:
            message_to_group += f"Ряд: {current_row}\n"
        message_to_group += f"Место: {current_place}"
        # \nПользователь: {message.from_user.username or message.from_user.id}
        bot.send_message(message.chat.id, "Уже идем к Вам") # Отправляем сообщение пользователю
    elif current_action == 'bar':
        message_to_group = f"Новый заказ из бара:\nЗаказ: {current_order}\nЗона: {current_zone}\n"
        if current_type:
            message_to_group += f"Тип: {current_type}\n"
        if current_row:
            message_to_group += f"Ряд: {current_row}\n"
        message_to_group += f"Место: {current_place}"
        # \nПользователь: {message.from_user.username or message.from_user.id}
        bot.send_message(message.chat.id, "Уже готовим") # Отправляем сообщение пользователю

    # Отправляем сообщение в группу
    bot.send_message(GROUP_ID, message_to_group) # Отправляем сообщение в группу
    bot.send_message(message.chat.id, "Пожалуйста, нажмите /start для нового заказа.")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back(message):
    global current_zone, current_type, current_row, current_place, current_action, current_order

    if current_zone and (current_type is None and current_row is None):
        start(message)
    elif current_type is None and current_row is None:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=create_main_menu())
    elif current_zone == "Желтая зона" and current_type is None:
        bot.send_message(message.chat.id, "Выберите зону:", reply_markup=create_zone_keyboard())
    elif current_zone == "Зеленая зона" and current_row is None:
        bot.send_message(message.chat.id, "Выберите зону:", reply_markup=create_zone_keyboard())
    elif current_zone:
        if current_action == 'hookah':
            bot.send_message(message.chat.id, "Выберите зону:", reply_markup=create_zone_keyboard())
        elif current_action == 'bar':
            bot.send_message(message.chat.id, "Напишите, пожалуйста, что Вам принести:")

# --- Запуск бота ---

if __name__ == '__main__':
    bot.infinity_polling()
