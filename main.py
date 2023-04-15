from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import datetime
import calendar
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = ""

def start(update, context):
    update.message.reply_text("Здравствуйте! Чтобы записаться на консультацию к детскому психологу Красновой Елене, нажмите /book_consultation")

def book_consultation(update, context):
    update.message.reply_text("Пожалуйста, укажите ваше имя и контактную информацию (например, номер телефона или адрес электронной почты) после имени")

def collect_user_data(update, context):
    user_data = update.message.text
    context.user_data["user_data"] = user_data
    update.message.reply_text("Отлично! Теперь выберите предпочтительную дату консультации")

    # Создание клавиатуры для выбора дат
    date_keyboard = []

    # Заполнение клавиатуры доступными датами
    interval = 7 # интервал в днях
    for i in range(interval):
        current_date = datetime.date.today() + datetime.timedelta(days=i)
        current_button = InlineKeyboardButton(current_date.strftime("%d/%m/%Y"), callback_data=current_date.strftime("%d/%m/%Y"))
        date_keyboard.append([current_button])

    context.user_data["date_keyboard"] = date_keyboard

    reply_markup = InlineKeyboardMarkup(date_keyboard)
    update.message.reply_text("Выберите дату:", reply_markup=reply_markup)

def select_date(update, context):
    selected_date = update.callback_query.data
    context.user_data["selected_date"] = selected_date
    update.callback_query.answer()

    update.callback_query.edit_message_text("Выбранная дата: {}\n\nТеперь выберите время.".format(selected_date))

    # Создание клавиатуры для выбора времени
    time_keyboard = []

    # Заполнение клавиатуры временными интервалами
    time_intervals = [
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00"
    ]
    
    for time in time_intervals:
        time_button = InlineKeyboardButton(time, callback_data=time)
        time_keyboard.append([time_button])

    reply_markup = InlineKeyboardMarkup(time_keyboard)
    update.callback_query.edit_message_text("Выберите время:", reply_markup=reply_markup)

def select_time(update, context):
    time_slot = update.callback_query.data
    context.user_data["time_slot"] = time_slot
    update.callback_query.answer()

    user_data = context.user_data["user_data"]
    date_str = context.user_data["selected_date"]
    time_str = context.user_data["time_slot"]

    # Отправка записи пользователем в канал
    bot = context.bot
    bot.send_message(chat_id="@fastlook", text="*Новая запись на консультацию:*\nПользователь: {}\nДата и время: {} в {}\n_для детского психолога Красновой Елены_".format(user_data, date_str, time_str), parse_mode="Markdown")

    update.callback_query.edit_message_text('Запись на консультацию сделана успешно! Мы свяжемся с вами для подтверждения. Ваши данные: \n\n{} - {} в {}'.format(user_data, date_str, time_str))

if __name__ == "__main__":
  updater = Updater(TOKEN, use_context=True)
  dp = updater.dispatcher
  dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("book_consultation", book_consultation))
dp.add_handler(MessageHandler(Filters.text, collect_user_data))

dp.add_handler(CallbackQueryHandler(select_date, pattern=r'^\d{2}/\d{2}/\d{4}$'))
dp.add_handler(CallbackQueryHandler(select_time, pattern=r'^\d{2}:\d{2}$'))
