import os
import telebot
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Servidor web que se adapta automaticamente à porta que a Render escolher
class FakeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Robo Online")

def run_web_server():
    # os.environ.get('PORT') pega a porta que a Render quiser usar de forma automática
    port = int(os.environ.get("PORT", 80))
    server = HTTPServer(('0.0.0.0', port), FakeServer)
    server.serve_forever()

# Inicia o servidor em segundo plano
Thread(target=run_web_server, daemon=True).start()

# Configuração oficial do seu bot do Telegram
TOKEN = "8751717795:AAHtRIJnEEOhKArso18kRfpBhb48BwUg4Ls"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! O robô Pele de Milhões está online e pronto para trabalhar!")

print("Robô iniciado com sucesso...")
bot.infinity_polling()
