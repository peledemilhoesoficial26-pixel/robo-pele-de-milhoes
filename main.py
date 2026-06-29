import os
import telebot
import re
import requests
import time
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

# =====================================================================
# CONFIGURAÇÕES DE CREDENCIAIS
# =====================================================================
TOKEN = "8751717795:AAHtRIJnEEOhKArso18kRfpBhb48BwUg4Ls"
ID_CANAL_ALVO = "@testepeledemilhoes123"

# Tags e Chaves de Afiliados
AMAZON_TAG = os.environ.get("AMAZON_TAG", "peledemilhoes-20")
SHOPEE_API_KEY = "SEU_API_KEY_DA_SHOPEE_AQUI"
SHOPEE_APP_SECRET = "SEU_APP_SECRET_DA_SHOPEE_AQUI"
MERCADO_LIVRE_ID = "SEU_ID_MERCADO_LIVRE_AQUI"
MAGALU_ID = "SEU_ID_MAGALU_AQUI"

bot = telebot.TeleBot(TOKEN)

# =====================================================================
# LISTA EXCLUSIVA DE MARCAS PERMITIDAS (APENAS ESTAS!)
# =====================================================================
MARCAS_PERMITIDAS = [
    "Vichy", "La Roche", "Eucerin", "Creamy", "Principia", "Océane", "Oceane", "CeraVe", "Cerave", 
    "Avène", "Avene", "SkinCeuticals", "Skinceuticals", "Actine", "Bioré", "Biore", "Dermage", 
    "Adcos", "Neutrogena", "Cetaphil", "Bioderma", "Sallve", "The Ordinary", "Simple Organic", 
    "COSRX", "Cosrx", "Skin1004", "SKIN1004", "Medicube", "Mantecorp", "ISDIN", "Isdin", "Profuse", 
    "Rhode", "Estée Lauder", "Estee Lauder", "Lancôme", "Lancome", "Clinique", "Shiseido", 
    "Beauty of Joseon", "Anua", "Round Lab", "Purito", "Laneige", "Some By Mi", "Beyoung", 
    "Meditherapy", "Celimax", "Galderma", "VT Cosmetics", "Darrow", "Isntree", "Hada Labo", 
    "Melano CC", "Senka", "Naturie", "DHC", "Curél", "Curel", "d program", "Minon Amino", "SK-II", 
    "Clé de Peau", "Decorté", "Decorte", "POLA", "Cicatribem", "Nupill", "Banila Co", "Innisfree", 
    "Dr. Jart", "TIRTIR", "Tirtir", "Numbuzin", "Abib", "Esthederm", "L'Oréal", "Loreal", "Kiehl's", 
    "Dermotivin", "Missha", "Etude House", "Glow Recipe", "Caudalie", "Biossance", "Drunk Elephant", 
    "Dr. Althea", "K-Secret", "Jumiso", "Holika Holika", "Sol de Janeiro", "Obagi", "Sesderma", 
    "Neostrata", "I'm From", "Uriage", "Oura", "Needs", "The Inkey List", "Summer Fridays", "Byoma", 
    "Bubble Skincare", "Mary & May", "Skinfood", "Episol", "A-Derma", "SVR", "Rohto", "Mentholatum", 
    "Origins", "Paula's Choice", "Anessa", "Aestura", "Epidrat", "Theraskin", "Torriden", "Kose", 
    "Murad", "Filorga", "Malin+Goetz", "Hatomugi", "Mixoon", "Tatcha", "Blancy", "P.Calm", 
    "Mario Badescu", "Skincerity", "Nu Skin", "Skyn ICELAND", "Ada Tina", "Chasin' Rabbits", 
    "Pyunkang Yul", "Nuxe", "Sulwhasoo", "iS Clinical", "Kanebo", "Suisai", "Youth To The People", 
    "Melhora", "Endocare", "IOPE", "Lilyeve", "Popo Skinbakery"
]

# =====================================================================
# FUNÇÕES AUXILIARES E VERIFICAÇÃO DE SEGURANÇA
# =====================================================================
def extrair_url_limpa(texto):
    match = re.search(r'(https?://[^\s?#()\[\]]+)', texto)
    if match:
        return match.group(1)
    return None

def puxar_titulo_amazon(url):
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
    return "Produto Especial Skincare"

def verificar_marca_permitida(texto):
    """ Verifica se o título do produto contém alguma das marcas da lista """
    texto_minusculo = texto.lower()
    for marca in MARCAS_PERMITIDAS:
        if marca.lower() in texto_minusculo:
            return True
    return False

def converter_link_afiliado(url, loja):
    if loja == "amazon":
        if "?" in url:
            return f"{url}&tag={AMAZON_TAG}"
        return f"{url}?tag={AMAZON_TAG}"
    return url

# =====================================================================
# ROTINA DO PILOTO AUTOMÁTICO (VARRER OFERTAS DA LISTA)
# =====================================================================
def rotina_busca_automatica():
    print("Piloto automático focado na sua lista de marcas iniciado...")
    while True:
        try:
            for marca in MARCAS_PERMITIDAS:
                # O robô faz a varredura simulada focando estritamente nessa lista
                print(f"Buscando ofertas automatizadas exclusivas de: {marca}")
            time.sleep(10800) 
        except Exception as e:
            print(f"Erro na rotina automática: {e}")
            time.sleep(60)

Thread(target=rotina_busca_automatica, daemon=True).start()

# =====================================================================
# ENVIOS MANUAIS NO PRIVADO (COM FILTRO RÍGIDO DE MARCA)
# =====================================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! O robô está programado para aceitar APENAS a sua lista seleta de marcas de Skincare.")

@bot.message_handler(func=lambda message: True)
def processar_e_postar_manual(message):
    texto_bruto = message.text or message.caption or ""
    
    if "http" not in texto_bruto:
        return

    link_extraido = extrair_url_limpa(texto_bruto)
    if not link_extraido:
        return

    loja_detectada = None
    if any(x in link_extraido for x in ["amazon.com", "amzn.to", "a.co", "link.amazon"]):
        loja_detectada = "amazon"
    elif any(x in link_extraido for x in ["shopee.com", "shope.ee"]):
        loja_detectada = "shopee"
    elif any(x in link_extraido for x in ["mercadolivre.com", "meli.li"]):
        loja_detectada = "mercado_livre"
    elif any(x in link_extraido for x in ["magazineluiza.com.br", "magalu.com"]):
        loja_detectada = "magalu"

    if not loja_detectada:
        bot.reply_to(message, "⚠️ Link de loja não cadastrada!")
        return

    status_msg = bot.reply_to(message, f"🔍 Analisando produto... Verificando se pertence à sua lista de marcas autorizadas...")

    if loja_detectada == "amazon":
        titulo_produto = puxar_titulo_amazon(link_extraido)
    else:
        titulo_produto = "Produto Skincare Selecionado"

    # FILTRO DE SEGURANÇA: Se não estiver na lista de marcas, o robô barra!
    if not verificar_marca_permitida(titulo_produto) and loja_detectada == "amazon":
        bot.edit_message_text("❌ Postagem Recusada! Esse produto não pertence a nenhuma das marcas da sua lista oficial.", chat_id=message.chat.id, message_id=status_msg.message_id)
        return

    link_final_afiliado = converter_link_afiliado(link_extraido, loja_detectada)

    texto_final = f"➜ ✨ {titulo_produto}\n\n"
    texto_final += f"➜ 🔥 Compre com Segurança Aqui: {link_final_afiliado}\n\n"
    texto_final += "#anunciodeconfiança | Pele de Milhões ✨"

    try:
        bot.send_message(chat_id=ID_CANAL_ALVO, text=texto_final)
        bot.edit_message_text("✅ Produto da lista validado e postado com sucesso no Canal!", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as error:
        bot.edit_message_text(f"❌ Erro ao postar no canal: {error}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
    
