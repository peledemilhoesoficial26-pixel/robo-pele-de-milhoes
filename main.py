import os
import telebot
import re
import requests
from bs4 import BeautifulSoup
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Servidor web para manter o robô online na Render
class FakeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Robo Online")

def run_web_server():
    port = int(os.environ.get("PORT", 80))
    server = HTTPServer(('0.0.0.0', port), FakeServer)
    server.serve_forever()

# Inicia o servidor em segundo plano
Thread(target=run_web_server, daemon=True).start()

# CONFIGURAÇÃO DO BOT
TOKEN = "8751717795:AAHtRIJnEEOhKArso18kRfpBhb48BwUg4Ls"
AMAZON_TAG = os.environ.get("AMAZON_TAG", "peledemilhoes-20")

# O ID do seu canal que descobrimos!
ID_CANAL_ALVO = "-1002446714088"

bot = telebot.TeleBot(TOKEN)

def extrair_url_limpa(texto):
    match = re.search(r'(https?://[^\s?#()\[\]]+)', texto)
    if match:
        return match.group(1)
    return None

def puxar_titulo_amazon(url):
    """ Entra na Amazon e descobre o nome do produto """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find(id="productTitle")
            if title_tag:
                return title_tag.get_text().strip()
    except Exception as e:
        print(f"Erro ao puxar título: {e}")
    return "Produto Especial"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Mandando links aqui, eu posto formatado direto no Canal de Ofertas!")

@bot.message_handler(func=lambda message: True)
def processar_e_postar_automatico(message):
    texto_bruto = message.text or message.caption or ""
    
    if "http" not in texto_bruto:
        return

    link_extraido = extrair_url_limpa(texto_bruto)
    if not link_extraido:
        return

    is_amazon = any(x in link_extraido for x in ["amazon.com", "amzn.to", "a.co", "link.amazon"])
    
    if not is_amazon:
        bot.reply_to(message, "⚠️ Por enquanto, a postagem automática está calibrada para links Amazon!")
        return

    status_msg = bot.reply_to(message, "🔄 Buscando dados na Amazon e gerando post... Aguarde!")

    # 1. Pega o título real do produto no site da Amazon
    titulo_produto = puxar_titulo_amazon(link_extraido)

    # 2. Transforma o link em Link de Afiliada
    if "?" in link_extraido:
        link_afiliada = f"{link_extraido}&tag={AMAZON_TAG}"
    else:
        link_afiliada = f"{link_extraido}?tag={AMAZON_TAG}"

    # 3. Monta o texto com as setinhas e formatação profissional
    texto_final = f"➜ {titulo_produto}\n\n"
    texto_final += f"➜ 🔥 Compre aqui: {link_afiliada}\n\n"
    texto_final += "#anúncio | Pele de Milhões ✨"

    try:
        # 4. Posta AUTOMATICAMENTE no seu canal
        bot.send_message(chat_id=ID_CANAL_ALVO, text=texto_final)
        bot.edit_message_text("✅ Postagem realizada com sucesso direto no Canal!", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as error:
        bot.edit_message_text(f"❌ Erro ao postar no canal. Erro: {error}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    print("Robô Postador Automático Ativo...")
    bot.infinity_polling()
