import os
import requests
import time
from flask import Flask, request
from bs4 import BeautifulSoup  # Para web scraping
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

app = Flask(__name__)

# Substitua pelo token do seu bot
TOKEN = '7417865916:AAHXHPos-KsIhLEeK3a6Jkt-DL9KS7kjnuQ'
bot = Bot(token=TOKEN)

# Dicionário para armazenar os links e preços
monitored_links = {}

# Função para monitorar preços
def check_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Exemplo para Amazon (alterar de acordo com o site)
    price_tag = soup.find(id='priceblock_ourprice')
    if price_tag:
        price = price_tag.get_text()
        return price
    return None

# Comando para adicionar um link
def add_link(update: Update, context):
    url = ' '.join(context.args)
    if url:
        monitored_links[url] = check_price(url)
        update.message.reply_text(f'Link adicionado: {url}')
    else:
        update.message.reply_text('Por favor, envie um link válido.')

# Comando para checar preços
def check_prices(update: Update, context):
    messages = []
    for url, last_price in monitored_links.items():
        current_price = check_price(url)
        if current_price != last_price:
            monitored_links[url] = current_price
            messages.append(f'Preço atualizado no link {url}: {current_price}')
        else:
            messages.append(f'Sem mudanças no link {url}.')
    
    update.message.reply_text('\n'.join(messages))

# Configuração do Updater e Dispatcher
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Comandos do bot
dispatcher.add_handler(CommandHandler("add", add_link))
dispatcher.add_handler(CommandHandler("check", check_prices))

# Iniciar o bot
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
