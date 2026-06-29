import os
import telebot
import re
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
SHOPEE_TAG = os.environ.get("SHOPEE_TAG", "")

bot = telebot.TeleBot(TOKEN)

# 1. LISTA SUPREMA DE SKINCARE
MARCAS_SKINCARE = [
    "vichy", "la roche-posay", "la roche posey", "eucerin", "creamy", "principia", "oceane", 
    "cerave", "avene", "skinceuticals", "actine", "biore", "dermage", "adcos", "neutrogena", 
    "cetaphil", "bioderma", "sallve", "the ordinary", "simple organic", "cosrx", "skin1004", 
    "medicube", "mantecorp", "episol", "epidrat", "blancy", "isdin", "profuse", "rhode", "estee lauder", 
    "lancome", "clinique", "shiseido", "beauty of joseon", "anua", "round lab", "purito", 
    "laneige", "some by mi", "beyoung", "meditherapy", "celimax", "galderma", "vt cosmetics", 
    "darrow", "isntree", "hada labo", "melano cc", "senka", "naturie", "hatomugi", "dhc", "curel", 
    "d program", "minon amino", "sk-ii", "cle de peau", "decorte", "pola", "cicatribem", 
    "nupill", "banila co", "innisfree", "dr. jart", "tirtir", "numbuzin", "abib", 
    "institut esthederm", "loreal", "l'oreal", "kiehl's", "kiehls", "dermotivin", "missha", 
    "etude house", "glow recipe", "caudalie", "biossance", "drunk elephant", "dr. althea", 
    "k-secret", "jumiso", "holika homika", "sol de janeiro", "obagi", "sesderma", "neostrata", 
    "i'm from", "uriage", "oura", "needs", "the inkey list", "summer fridays", "byoma", 
    "bubble", "mary & may", "skinfood", "a-derma", "aderma", "svr", "rohto", "skin aqua", 
    "origins", "paula's choice", "paulas choice", "anessa", "aestura", "theraskin", 
    "torriden", "kose", "softymo", "murad", "malin", "filorga", "mixoon", "tatcha", 
    "p.calm", "mario badescu", "skincerity", "nu skin", "skyn iceland", "ada tina", 
    "chasin rabbits", "pyunkang yul", "nuxe", "sulwhasoo", "is clinical", "isclinical", 
    "kanebo", "suisai", "youth to the people", "melora", "endocare"
]

# 2. LISTA COMPLETA DE SITES PARCEIROS PERMITIDOS
SITES_PERMITIDOS = [
    "amazon.com.br", "amazon.com", "amzn.to", "a.co", "link.amazon",
    "shopee.com.br", "shopee.com", "shope.ee",
    "mercadolivre.com.br", "mercadolivre.com", "meli.li",
    "monetizze.com.br", "casasbahia.com.br", "ponto.com.br", 
    "extra.com.br", "carrefour.com.br", "magazineluiza.com.br", 
    "magazinevoce.com.br", "americanas.com.br", "americanas.com",
    "epocacosmeticos.com.br", "belezanaweb.com.br", "sephora.com.br", 
    "ikesaki.com.br", "natura.com.br", "oboticario.com.br", "avon.com.br",
    "drogaraia.com.br", "drogasil.com.br", "drogariasaopaulo.com.br", 
    "drogariaspacheco.com.br", "paguemenos.com.br", "panvel.com",
    "drogariaaraujo.com.br", "drogariavenancio.com.br"
]

def extrair_url_limpa(texto):
    match = re.search(r'(https?://[^\s?#()\[\]]+)', texto)
    if match:
        return match.group(1)
    return texto.strip()

def verificar_se_e_skincare(texto_completo):
    texto_minusculo = texto_completo.lower()
    for marca in MARCAS_SKINCARE:
        if marca in texto_minusculo:
            return True
    return False

def verificar_site_permitido(url_produto):
    url_minuscula = url_produto.lower()
    for site in SITES_PERMITIDOS:
        if site in url_minuscula:
            return True
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! O robô Pele de Milhões está ativo e atualizado!")

@bot.message_handler(func=lambda message: True)
def processar_link_oferta(message):
    texto_bruto = message.text or ""
    texto_para_analise = texto_bruto

    if message.caption:
        texto_para_analise += " " + message.caption

    if "http" not in texto_para_analise:
        return
        
    link_limpo = extrair_url_limpa(texto_bruto)
        
    if not verificar_site_permitido(link_limpo):
        bot.reply_to(message, f"⚠️ O site analisado ({link_limpo}) não faz parte das nossas lojas parceiras autorizadas.")
        return

    if not verificar_se_e_skincare(texto_para_analise):
        bot.reply_to(message, "❌ Link recusado! O produto não pertence a nenhuma marca de skincare da lista.")
        return

    link_final = link_limpo
    mensagem_sucesso = "✅ **PRODUTO VALIDADO!**\n\n"

    # Conversão Automática - AMAZON
    if any(x in link_limpo for x in ["amazon.com", "amzn.to", "a.co", "link.amazon"]):
        if "?" in link_limpo:
            link_final = f"{link_limpo}&tag={AMAZON_TAG}"
        else:
            link_final = f"{link_limpo}?tag={AMAZON_TAG}"
        mensagem_sucesso += f"🛒 **Link de Afiliada Amazon Gerado:**\n{link_final}"

    # Conversão Automática - SHOPEE
    elif "shopee.com" in link_limpo or "shope.ee" in link_limpo:
        if SHOPEE_TAG:
            link_final = f"https://shope.ee/ats/{SHOPEE_TAG}?url={link_limpo}"
            mensagem_sucesso += f"🛍️ **Link de Afiliada Shopee Gerado:**\n{link_final}"
        else:
            mensagem_sucesso += f"🛍️ **Link Shopee Aprovado!**\nUse o app da Shopee para converter:\n{link_limpo}"

    else:
        mensagem_sucesso += f"✨ **Link de Loja Parceira Aprovado!**\nGere manualmente na sua plataforma:\n{link_limpo}"

    bot.reply_to(message, mensagem_sucesso, parse_mode="Markdown")

if __name__ == "__main__":
    print("Robô reiniciado com sucesso...")
    bot.infinity_polling()
