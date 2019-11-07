import telebot
import requests

API_TOKEN = 'My_Token'
WEBHOOK_HOST = 'My_ip'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

def create_bot():
    bot = telebot.TeleBot(API_TOKEN)

    # Handle '/start' and '/help'
    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        bot.reply_to(message, 'Type /id "your_username" to register yourself')

    @bot.message_handler(commands=['id', 'user'])
    def register_user(message):
        usr = message.text.split(' ')[1]
        tel_id = str(message.from_user)
        reply = requests.post('localhost:5000/bot/register?username='+usr+'&tel_id='+tel_id)
        if reply.status_code == 200:
            bot.reply_to(message, 'User registered')
        else:
            bot.reply_to(message, 'Invalid username')

    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    return bot