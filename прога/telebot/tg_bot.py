import telebot
from telebot import types
import json
import time
import os
from dotenv import load_dotenv
# load env file
load_dotenv(".env")

# create TeleBot with API key
bot = telebot.TeleBot(os.getenv("BOT_KEY"))

# create buttons and menus
keyboard_menu = types.InlineKeyboardMarkup(row_width=2)
key_markets = types.InlineKeyboardButton(text='Площадки', callback_data='markets_query')
key_category = types.InlineKeyboardButton(text='Категории', callback_data='categories_query')
key_regions = types.InlineKeyboardButton(text='Регионы', callback_data='districts_query')
key_start_price = types.InlineKeyboardButton(text='Начальная стоимость', callback_data='start_price_query')
key_end_price = types.InlineKeyboardButton(text='Конечная стоимость', callback_data='end_price_query')
key_search = types.InlineKeyboardButton(text='Найти лоты', callback_data='search_query')
key_text = types.InlineKeyboardButton(text='Поиск по словам', callback_data='search_query_text')
keyboard_menu.add(key_start_price, key_end_price, key_markets, key_regions, key_category, key_text)
keyboard_menu.add(key_search)

keyboard_districts = types.InlineKeyboardMarkup(row_width=1)
key_1 = types.InlineKeyboardButton(text='Центральный федеральный округ', callback_data='regions_query_1')
key_2 = types.InlineKeyboardButton(text='Северо-Западный федеральный округ', callback_data='regions_query_2')
key_3 = types.InlineKeyboardButton(text='Южный федеральный округ', callback_data='regions_query_3')
key_4 = types.InlineKeyboardButton(text='Северо-Кавказский федеральный округ', callback_data='regions_query_4')
key_5 = types.InlineKeyboardButton(text='Приволжский федеральный округ', callback_data='regions_query_5')
key_6 = types.InlineKeyboardButton(text='Уральский федеральный округ', callback_data='regions_query_6')
key_7 = types.InlineKeyboardButton(text='Сибирский федеральный округ', callback_data='regions_query_7')
key_8 = types.InlineKeyboardButton(text='Дальневосточный федеральный округ', callback_data='regions_query_8')
keyboard_districts.add(key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8)

keyboard_prices_start = types.InlineKeyboardMarkup(row_width=2)
key_1 = types.InlineKeyboardButton(text='Стартовая цена (от)', callback_data='start_query_from')
key_2 = types.InlineKeyboardButton(text='Стартовая цена (до)', callback_data='start_query_to')
keyboard_prices_start.add(key_1, key_2)

keyboard_prices_current = types.InlineKeyboardMarkup(row_width=2)
key_1 = types.InlineKeyboardButton(text='Текущая цена (от)', callback_data='current_query_from')
key_2 = types.InlineKeyboardButton(text='Текущая цена (до)', callback_data='current_query_to')
keyboard_prices_current.add(key_1, key_2)

# dict {UserID: UserParams}
user_data = {}


def make_back_from_menu(call):
    alert_text = f"Вы настроили {call.message.text.split()[1]}!"
    bot.answer_callback_query(call.id, show_alert=True, text=alert_text)
    bot.edit_message_text(text="Настрой фильтр", chat_id=call.message.chat.id, message_id=call.message.message_id,
                          reply_markup=keyboard_menu)


def accepted(message):
    message = bot.send_message(chat_id=message.chat.id, text='Принято')
    bot.edit_message_text(text="Что-то еще настроим?", chat_id=message.chat.id, message_id=message.message_id,
                          reply_markup=keyboard_menu)


def make_text_query(call):
    message = bot.edit_message_text(text="Введи поисковой запрос", chat_id=call.message.chat.id,
                                    message_id=call.message.message_id)
    bot.register_next_step_handler(message, accepted)


class User:

    def __init__(self):
        """load filter params template from file"""
        with open("template_params.json", 'r', encoding='utf-8') as file:
            template_params = json.load(file)
        with open("filter_template.json", 'r', encoding='utf-8') as file2:
            filter_params = json.load(file2)
        # __dict__()
        self.params = template_params.copy()
        self.filter = filter_params.copy()
        self.changed = False
        self.webWorker = ''

    def get_price_start_from(self, message):
        # validate message
        if message.text.isdigit():
            if int(message.text) > int(self.filter["start_price"]["to"]):
                message = bot.send_message(chat_id=message.chat.id, text='Не принято')
                bot.edit_message_text(text="Установите начальную стоимость меньше конечной!", chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard_menu)
            else:
                accepted(message)
                self.filter["start_price"]["from"] = message.text
        # try again
        else:
            message = bot.send_message(chat_id=message.chat.id, text='Не принято')
            bot.edit_message_text(text="Введена некорректная стоимость! Введите ее заново", chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard_prices_start)

    def get_price_start_to(self, message):
        # validate message
        if message.text.isdigit():
            if int(self.filter["start_price"]["from"]) > int(message.text):
                message = bot.send_message(chat_id=message.chat.id, text='Не принято')
                bot.edit_message_text(text="Установите начальную стоимость меньше конечной!",
                                      chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard_menu)
            else:
                accepted(message)
                self.filter["start_price"]["to"] = message.text
        # try again
        else:
            message = bot.send_message(chat_id=message.chat.id, text='Не принято')
            bot.edit_message_text(text="Введена некорректная стоимость! Введите ее заново", chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard_prices_start)

    def get_price_current_from(self, message):
        # validate message
        if message.text.isdigit():
            if int(message.text) > int(self.filter["current_price"]["to"]):
                message = bot.send_message(chat_id=message.chat.id, text='Не принято')
                bot.edit_message_text(text="Установите начальную стоимость меньше конечной!",
                                      chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard_menu)
            else:
                accepted(message)
                self.filter["current_price"]["from"] = message.text
        # try again
        else:
            message = bot.send_message(chat_id=message.chat.id, text='Не принято')
            bot.edit_message_text(text="Введена некорректная стоимость! Введите ее заново", chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard_prices_current)

    def get_price_current_to(self, message):
        # validate message
        if message.text.isdigit():
            if int(self.filter["current_price"]["from"]) > int(message.text):
                message = bot.send_message(chat_id=message.chat.id, text='Не принято')
                bot.edit_message_text(text="Установите текущую начальную стоимость меньше конечной!",
                                      chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard_menu)
            else:
                accepted(message)
                self.filter["current_price"]["to"] = message.text
        # try again
        else:
            message = bot.send_message(chat_id=message.chat.id, text='Не принято')
            bot.edit_message_text(text="Введена некорректная стоимость! Введите ее заново", chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard_prices_current)

    def make_price(self, call):
        """price handler"""
        if call.data.split("_")[0] == "start":
            if call.data.split("_")[2] == "from":
                text = "Введи стартовую стоимость (от)"
                message = bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                                                message_id=call.message.message_id)
                bot.register_next_step_handler(message, self.get_price_start_from)
            else:
                text = "Введи стартовую стоимость (до)"
                message = bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                                                message_id=call.message.message_id)
                bot.register_next_step_handler(message, self.get_price_start_to)
        else:
            if call.data.split("_")[2] == "from":
                text = "Введи текущую стоимость (от)"
                message = bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                                                message_id=call.message.message_id)
                bot.register_next_step_handler(message, self.get_price_current_from)
            else:
                text = "Введи текущую стоимость (до)"
                message = bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                                                message_id=call.message.message_id)
                bot.register_next_step_handler(message, self.get_price_current_to)

    def make_menu_from_districts(self, call):
        """draw menu for districts & regions"""
        keys_list = []
        keyboard_filter_params = types.InlineKeyboardMarkup(row_width=2)

        for district in self.params.get("districts"):
            if "query" in call.data:
                if self.params.get("districts").get(district).get("code") == call.data.split("_")[2]:
                    selected_regions = self.params.get("districts").get(district).get("regions")
                    break
            else:
                for district in self.params.get("districts"):
                    if int(call.data.split("_")[1]) in self.params.get("districts").get(district).get("regions"):
                        selected_regions = self.params.get("districts").get(district).get("regions")

        for region in self.params.get("regions"):
            if int(self.params.get("regions").get(region)[0]) in selected_regions:
                if self.params.get("regions").get(region)[1]:
                    btn_text = f"✅{region}"
                else:
                    btn_text = region
                key = types.InlineKeyboardButton(text=btn_text,
                                                 callback_data=f"btnRegions_{self.params.get('regions').get(region)[0]}")

                keys_list.append(key)

        key = types.InlineKeyboardButton(text="◀️Назад", callback_data='back_menu')
        keys_list.append(key)
        keyboard_filter_params.add(*keys_list)
        bot.edit_message_text(text='Выбери параметр', chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=keyboard_filter_params)

    def make_menu(self, call):
        """draw menu with selected params"""
        keys_list = []

        filter_parameter = call.data.split("_")[0]

        if "btn" in filter_parameter:
            filter_parameter = filter_parameter[3:].lower()
        row_width = 2

        if call.data == "markets_query" or "btnMarkets" in call.data:
            row_width = 1

        keyboard_filter_params = types.InlineKeyboardMarkup(row_width=row_width)
        for item in self.params.get(filter_parameter).keys():
            if self.params.get(filter_parameter).get(item)[1]:
                btn_text = f"✅{item}"
            else:
                btn_text = item
            buf = self.params.get(filter_parameter).get(item)[0]
            callback_data = f"btn{filter_parameter.capitalize()}_{buf}"
            key = types.InlineKeyboardButton(text=btn_text,
                                             callback_data=callback_data)
            keys_list.append(key)
        key = types.InlineKeyboardButton(text="◀️Назад", callback_data='back_menu')
        keys_list.append(key)
        keyboard_filter_params.add(*keys_list)
        bot.edit_message_text(text='Выбери параметр', chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard_filter_params)


@bot.message_handler(commands=['start'])
def get_start(message):
    """bot start message"""
    bot.send_message(message.from_user.id, text="Добро пожаловать в Торги по банкротству РФ!")
    bot.send_message(message.from_user.id, text="Давай настроим фильтр?", reply_markup=keyboard_menu)
    # add new user at dict
    user_data[message.chat.id] = User()


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    """callback push button"""
    current_user = user_data.get(call.message.chat.id) # get user from dict
    if current_user:
        if call.data == "markets_query" or call.data == "categories_query":
            current_user.make_menu(call)
        elif call.data == "districts_query":
            bot.edit_message_text(text='Выбери округ', chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=keyboard_districts)
        elif "regions_query" in call.data:
            current_user.make_menu_from_districts(call)
        elif call.data == "start_price_query":
            bot.edit_message_text(text='Выбери', chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=keyboard_prices_start)
        elif call.data == "end_price_query":
            bot.edit_message_text(text='Выбери', chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=keyboard_prices_current)
        elif "from" in call.data or "to" in call.data:
            current_user.make_price(call)
        elif call.data == "search_query":
            bot.answer_callback_query(call.id, show_alert=True, text="В разработке!")
        elif call.data == "search_query_text":
            make_text_query(call)
        elif call.data == "back_menu":
            make_back_from_menu(call)
        elif call.data.split("_")[0] == "btnCategories" or call.data.split("_")[0] == "btnMarkets" \
                or call.data.split("_")[0] == "btnRegions":
            selected_region = ''
            current_name = ''
            filter_parameter = call.data.split("_")[0][3:].lower()

            if call.data.split("_")[0] == "btnRegions":
                for district in current_user.params.get("districts"):
                    if int(call.data.split("_")[1]) in current_user.params.get("districts").get(district).get(
                            "regions"):
                        selected_region = current_user.params.get("districts").get(district).get("regions")

                        break
            if not selected_region:
                current_params = current_user.params.get(f"{filter_parameter}")
                for k, v in current_params.items():
                    if str(v[0]) == call.data.split("_")[1]:
                        current_name = k
                        break
                if not current_user.params.get(f"{filter_parameter}").get(current_name)[1]:
                    current_user.params[f"{filter_parameter}"][current_name][1] = True
                    if current_user.params[f"{filter_parameter}"][current_name][0] not in  current_user.filter[f"{filter_parameter}"]:
                        current_user.filter[f"{filter_parameter}"].append(current_user.params[f"{filter_parameter}"][current_name][0])
                    current_user.make_menu(call)
                else:
                    current_user.params[f"{filter_parameter}"][current_name][1] = False
                    if current_user.params[f"{filter_parameter}"][current_name][0] in current_user.filter[f"{filter_parameter}"]:
                        current_user.filter[f"{filter_parameter}"].remove(current_user.params[f"{filter_parameter}"][current_name][0])
                    current_user.make_menu(call)
            else:
                current_params = current_user.params.get("regions")
                for k, v in current_params.items():
                    if str(v[0]) == call.data.split("_")[1] and int(v[0]) in selected_region:
                        current_name = k
                        break
                if not current_user.params.get("regions").get(current_name)[1]:
                    current_user.params["regions"][current_name][1] = True
                    if current_user.params["regions"][current_name][0] not in current_user.filter["regions"]:
                        current_user.filter["regions"].append(current_user.params["regions"][current_name][0])
                    current_user.make_menu_from_districts(call)
                else:
                    current_user.params["regions"][current_name][1] = False
                    if current_user.params["regions"][current_name][0] in current_user.filter["regions"]:
                        current_user.filter["regions"].remove(current_user.params["regions"][current_name][0])
                    current_user.make_menu_from_districts(call)
    # user not in base
    else:
        # bot start message
        bot.send_message(chat_id=call.message.chat.id, text='Введите /start')

    # change user params in the dict
    user_data[call.message.chat.id] = current_user


# bot start
bot.polling(none_stop=True, interval=0)
