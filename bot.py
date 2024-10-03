import os
import requests
import time
import schedule
from flask import Flask, request
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import CommandHandler, ApplicationBuilder
from threading import Thread

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

    price_tag = soup.find(id='priceblock_ourprice')
    if price_tag:
        price = price_tag.get_text()
        return price
    return None

# Função para verificar todos os preços
def check_all_prices():
    messages = []
    for url, last_price in monitored_links.items():
        current_price = check_price(url)
        if current_price != last_price:
            monitored_links[url] = current_price
            messages.append(f'Preço atualizado no link {url}: {current_price}')
        else:
            messages.append(f'Sem mudanças no link {url}.')

    for message in messages:
        bot.send_message(chat_id='1704610309', text=message)

# Agendamento para verificar os preços a cada 30 minutos
def schedule_price_check():
    schedule.every(30).minutes.do(check_all_prices)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Comando para adicionar um link
def add_link(update: Update, context):
    url = ' '.join(context.args)
    if url:
        monitored_links[url] = check_price(url)
        update.message.reply_text(f'Link adicionado: {url}')
    else:
        update.message.reply_text('Por favor, envie um link válido.')

# Comando para checar preços manualmente
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

# Configuração do Application
application = ApplicationBuilder().token(TOKEN).build()

# Comandos do bot
application.add_handler(CommandHandler("add", add_link))
application.add_handler(CommandHandler("check", check_prices))

# Iniciar o bot
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.process_update(update)
    return "ok"

if __name__ == '__main__':
    # Inicie a thread de agendamento
    thread = Thread(target=schedule_price_check)
    thread.start()

    PORT = int(os.environ.get('PORT', 5000))
    application.run_polling()
