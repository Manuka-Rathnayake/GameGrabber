import discord 
import os
from dotenv import load_dotenv
import requests
import json
from epicstore_api.api import EpicGamesStoreAPI
import schedule
import time
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

current_time = datetime.utcnow()
next_thursday = current_time + timedelta(days=(3 - current_time.weekday()) % 7)
next_thursday = next_thursday.replace(hour=20, minute=40, second=0, microsecond=0)


def run_free_games_check():
     free_games = get_free_games()
     free_game_titles = get_free_game_titles(free_games)

     if free_game_titles:
        response = "\n".join(free_game_titles)
        channel = bot.get_channel(1144557263151956062) 
        bot.loop.create_task(channel.send(f"This week free games:\n{response}"))



scheduler.add_job(run_free_games_check, 'interval', weeks=1, start_date=next_thursday)


def get_free_games(allow_countries: str = None):
    api = EpicGamesStoreAPI()
    free_games_data = api.get_free_games(allow_countries)
    return free_games_data


def get_free_game_titles(free_games_data):
    game_title = []
    games = free_games_data['data']['Catalog']['searchStore']['elements']
    for game in games:
        categories = game.get('categories', [])
        if categories and categories[0].get('path') == 'freegames':
            title = game['title']
            game_title.append(title)
    return game_title


load_dotenv()

Discord_TOKEN = os.getenv("TOKEN")


bot = discord.Client(intents=discord.Intents().all())


@bot.event 
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    


@bot.event
async def on_message(message):
     if message.author == bot.user:
          return
     

     if message.content.startswith('$epicfree'):
          free_games = get_free_games()
          free_game_titles = get_free_game_titles(free_games)

          if free_game_titles:
              response = "\n".join(free_game_titles)
              await message.channel.send(f"Currently free games:\n{response}")



     if message.content.startswith('$hello'):
        await message.channel.send('Hello')

     if message.content.startswith('!getprice'):
         game_title = message.content[len('!getprice '):]

         cheapshark_api = f'https://www.cheapshark.com/api/1.0/games?title={game_title}'
         response = requests.get(cheapshark_api)
         data = response.json()

         if data:
             steam_id = data[0]['steamAppID']

             steam_api = f'https://store.steampowered.com/api/appdetails?appids={steam_id}&cc=us&filters=price_overview'
             steam_response = requests.get(steam_api)
             steam_data = steam_response.json()

             if steam_data and str(steam_id) in steam_data:
                 price = steam_data[str(steam_id)]['data']['price_overview']
                 currency = price['currency']
                 final_price = price['final_formatted']
                 await message.channel.send(f"The current price of the {game_title} on steam is {final_price}")



bot.run(Discord_TOKEN)
while True:
    schedule.run_pending()
    time.sleep(1)
