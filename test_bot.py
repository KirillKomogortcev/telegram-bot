import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# === НАСТРОЙКИ ===
TOKEN = '8318284839:AAFXmBDloBgzvvABboSHOx56Ng_dy_oovwo'
CHANNEL_USERNAME = '@AnastasyaSavkinaChannel'
GIFT_FILE_PATH = 'gift.pdf'

bot = telebot.TeleBot(TOKEN)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---


def create_subscription_keyboard():
    """Создает inline-клавиатуру с кнопками 'Подписаться' и 'Я подписался'."""
    keyboard = InlineKeyboardMarkup()
    btn_subscribe = InlineKeyboardButton(
        "Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    btn_check = InlineKeyboardButton("Я подписался",
                                     callback_data='check_subscription')
    keyboard.add(btn_subscribe, btn_check)
    return keyboard


def is_user_subscribed(user_id):
    """
    Проверяет, подписан ли пользователь на канал.

    Args:
        user_id (int): ID пользователя Telegram.

    Returns:
        bool: True, если пользователь подписан ('member', 'administrator', 'creator'),
              False в противном случае или при ошибке.
    """
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = chat_member.status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        # Логируем ошибку, если нужно (например, print(f"Ошибка проверки: {e}"))
        # Возвращаем False, если проверка не удалась
        return False


def send_welcome_message(chat_id, first_name):
    """Отправляет пользователю приветственное сообщение с инструкциями и кнопками."""
    welcome_text = (
        f"✨ Привет, <b>{first_name}</b>!\n\n"
        f"Я рад(а), что ты здесь! 🤗\n\n"
        f"У меня для тебя есть <b>особенный подарок</b> — "
        f"эксклюзивный PDF-файл, полный полезной и интересной информации.\n\n"
        f"Но сначала, давай дружить! Подпишись на мой канал 👇\n"
        f"👉 {CHANNEL_USERNAME}\n\n"
        f"После подписки нажми кнопку <i>\"Я подписался\"</i> — и твой подарок будет у тебя! 🎁"
    )
    keyboard = create_subscription_keyboard()
    bot.send_message(chat_id,
                     welcome_text,
                     reply_markup=keyboard,
                     parse_mode='HTML')


def send_gift(chat_id, first_name):
    """Отправляет пользователю подарочный PDF-файл."""
    gift_caption = (
        f"🎉 Ура, {first_name}! Поздравляю с подпиской! 🎉\n\n"
        f"Твой <b>подарок</b> — эксклюзивный PDF-файл — уже прикреплён к этому сообщению.\n\n"
        f"Наслаждайся содержимым! 📚✨")
    try:
        with open(GIFT_FILE_PATH, 'rb') as pdf_file:
            bot.send_document(chat_id,
                              pdf_file,
                              caption=gift_caption,
                              parse_mode='HTML',
                              visible_file_name='Подарок_от_Анастасии.pdf')
        return True
    except FileNotFoundError:
        print(f"Ошибка: файл {GIFT_FILE_PATH} не найден.")
        return False
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        return False


def send_reminder_message(chat_id, message_id, first_name):
    """Редактирует сообщение, напоминая пользователю о подписке."""
    reminder_text = (
        f"❌ Привет, {first_name}!\n\n"
        f"К сожалению, я не вижу тебя в подписчиках канала <b>{CHANNEL_USERNAME}</b>.\n\n"
        f"Чтобы получить подарок, обязательно подпишись по ссылке 👇\n"
        f"Затем вернись сюда и нажми 'Я подписался' снова! 🔄")
    keyboard = create_subscription_keyboard()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=reminder_text,
                          reply_markup=keyboard,
                          parse_mode='HTML')


def send_error_message(chat_id, message_id, first_name):
    """Редактирует сообщение, информируя пользователя об ошибке."""
    error_text = (
        f"⚠️ Ой, {first_name}! Что-то пошло не так при проверке подписки.\n\n"
        f"Пожалуйста, убедись, что ты <b>подписан(а)</b> на канал <i>{CHANNEL_USERNAME}</i>, "
        f"и нажми кнопку 'Я подписался' снова.\n\n"
        f"Если проблема повторяется, возможно, стоит выйти и снова зайти в Telegram и повторить попытку."
    )
    keyboard = create_subscription_keyboard()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=error_text,
                          reply_markup=keyboard,
                          parse_mode='HTML')


# --- ОБРАБОТЧИКИ КОМАНД И КНОПОК ---


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    send_welcome_message(message.chat.id, first_name)


@bot.callback_query_handler(
    func=lambda call: call.data == 'check_subscription')
def handle_check_subscription(call):
    """Обработчик нажатия на кнопку 'Я подписался'."""
    user_id = call.from_user.id
    first_name = call.from_user.first_name
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Проверяем подписку, используя отдельную функцию
    if is_user_subscribed(user_id):
        # Успешная подписка - отправляем подарок
        if send_gift(chat_id, first_name):
            bot.answer_callback_query(call.id, "Подарок отправлен! 🎁")
        else:
            # Если не удалось отправить файл, информируем об ошибке
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=
                f"❌ Извините, {first_name}, не удалось отправить подарок. Попробуйте позже."
            )
            bot.answer_callback_query(call.id, "Ошибка отправки файла.")
    else:
        # Подписка не найдена или ошибка при проверке
        send_reminder_message(chat_id, message_id, first_name)
        bot.answer_callback_query(call.id,
                                  "Подпишись на канал и попробуй снова! 📢")


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
