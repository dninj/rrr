import telebot
from config import *
from logic import *
import os


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды:
/show_city <название_города> - Показать город на карте.
/remember_city <название_города> - Запомнить город.
/show_my_cities - Показать все запомненные города на карте.
""")


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split(maxsplit=1)[1:] # корректное получение названия города
    if not city_name:
        bot.send_message(message.chat.id, "Введите название города после команды /show_city")
        return

    city_name = city_name[0] # извлечение строки из списка
    coordinates = manager.get_coordinates(city_name)
    if coordinates:
        manager.create_graph("single_city_map.png", [city_name])
        with open("single_city_map.png", "rb") as map_file:
            bot.send_photo(message.chat.id, map_file)
        os.remove("single_city_map.png") # удаляем временный файл
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split(maxsplit=1)[1:] # корректное получение названия города
    if not city_name:
        bot.send_message(message.chat.id, "Введите название города после команды /remember_city")
        return
    city_name = city_name[0] # извлечение строки из списка

    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if cities:
        manager.create_graph("my_cities_map.png", cities)
        with open("my_cities_map.png", "rb") as map_file:
            bot.send_photo(message.chat.id, map_file)
        os.remove("my_cities_map.png") # удаляем временный файл

    else:
        bot.send_message(message.chat.id, "Вы еще не добавили ни одного города.")



if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table() # Создаем таблицу при запуске бота
    bot.polling()
