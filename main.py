import telebot

TOKEN = "8751717795:AAHtRIJnEEOhKArso18kRfpBhb48BwUg4Ls"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! O robô Pele de Milhões está online e pronto para trabalhar!")

print("Robô iniciado com sucesso...")
bot.infinity_polling()
