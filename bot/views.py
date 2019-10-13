from django.shortcuts import render

# -*- coding: utf8 -*-

import json
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import OrderedWebhook, Webhook


import urllib3

from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.http import HttpResponse
from django.views.generic import View

from django.utils.decorators import method_decorator
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
import os

from base.models import Person, Summary

from datetime import datetime, date
import time

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
#bot.deleteWebhook()
bot.setWebhook('https://klishin16.pythonanywhere.com/bot/bot/{bot_token}/'.format(bot_token="blat"),  max_connections=3)
print(bot.getMe())

current_profession = "" #текущая профессия
current_city = ""
cur_page = 0 #текущая страница в списке кандидатов
last_message_id = ""

persons_on_page = 2 #число кандидатов на одной странице списка

@csrf_exempt
def inc(request, bot_token):
    payload = json.loads(request.body.decode('utf-8'))
    print(request.body.decode('utf-8'))
    hook.run_as_thread()
    hook.feed(payload)
    time.sleep(3)   
    return JsonResponse({}, status=200)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(msg['text'])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me', callback_data='press')],
               ])
    cmd = msg['text'].lower()

    if(cmd == "поиск по городам"):
        cities = Summary.objects.all().values("city").distinct()
        cities_buttons = []
        inside_items = 0
        inside_list = []
        for city in cities:
            if (inside_items < 2):
                inside_list.append(InlineKeyboardButton(text=city['city'], callback_data="city_{}".format(city['city'])))
                inside_items = inside_items + 1
            else:
                cities_buttons.append(inside_list)
                inside_list = []
                inside_list.append(InlineKeyboardButton(text=city['city'], callback_data="city_{}".format(city['city'])))
                inside_items = 1
        if (inside_items > 0):
            cities_buttons.append(inside_list)
        print(cities_buttons)

        city_keyboard = InlineKeyboardMarkup(inline_keyboard=cities_buttons)
        bot.sendMessage(chat_id, "Выберите ваш город:", reply_markup=city_keyboard)

    elif(cmd == "поиск по профессиям"):
        professions = Summary.objects.all().values("title").distinct()
        professions_buttons = []
        for profession in professions:
            print(profession)
            professions_buttons.append([InlineKeyboardButton(text=profession['title'], callback_data="profession_{}".format(profession['title'])), ])
        professions_keyboard = InlineKeyboardMarkup(inline_keyboard=professions_buttons)
        bot.sendMessage(chat_id, "Выберите профессию:", reply_markup=professions_keyboard)


    elif(cmd == "img"):
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        my_file = os.path.join(THIS_FOLDER, 'img1.jpg')
        print(my_file)
        bot.sendPhoto(chat_id, open(my_file, 'rb'))

    elif(cmd.find("city:") != -1 and len(cmd) > 5):
        _, c = cmd.split(':')
        query = Person.objects.filter(city=c)
        if not query:
            bot.sendMessage(chat_id, "К сожалению ничего не найдено", reply_markup=keyboard)
        else:
            bot.sendMessage(chat_id, "Результаты по запросу: {}".format(c))
            for profile in query:
                bot.sendMessage(chat_id, profile.name)

    else:
        #bot.sendMessage(chat_id, "You said: {}".format(cmd))
        bot.sendMessage(chat_id, 'Выберите тип поиска:',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Поиск по городам"), KeyboardButton(text="Поиск по профессиям")]
                                ]
                            ))

def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print ('Inline Query:', query_id, from_id, query_string)

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    telepot.deleteMessage(telepot.message_identifier(msg)) #возможное улучшение
    #content_type, chat_type, chat_id = telepot.glance(msg)
    #print ('Callback Query:', query_id, from_id, query_data)
    bot.answerCallbackQuery(query_id, text='Got it!')
    if ("city_" in query_data):

        global current_city
        global current_profession
        global cur_page
        global persons_on_page  

        if (query_data[5:] != "back_page" and query_data[5:] != "next_page"):
            if (current_city != query_data[5:]): #если текущий город еще не выбран
                current_city = query_data[5:]
                cur_page = 0 #сбрасываем страницы вывода на 1
        elif (query_data[5:] == "back_page"):
            cur_page = cur_page - 1
            if (cur_page < 0): cur_page = 0
        else:
            cur_page = cur_page + 1

        query = Summary.objects.filter(city=current_city)
            
        if not query:
            bot.sendMessage(from_id, "К сожалению ничего не найдено")
        else:
            pages_list = []
            profiles_on_page_list = []
            persons_num = 0
            for profile in query:
                if (persons_num < persons_on_page):
                    profiles_on_page_list.append([InlineKeyboardButton(text="{0} {1} \n{2}".format(profile.name, profile.second, profile.title), callback_data="person_{0}_{1}".format(profile.name, profile.second))])
                    persons_num = persons_num + 1
                else:
                    pages_list.append(profiles_on_page_list)
                    profiles_on_page_list = []
                    profiles_on_page_list.append([InlineKeyboardButton(text="{0} {1} \n{2}".format(profile.name, profile.second, profile.title), callback_data="person_{0}_{1}".format(profile.name, profile.second))])
                    persons_num = 1
            if (persons_num > 0):
                pages_list.append(profiles_on_page_list)

            page = pages_list[cur_page]
            control_buttons = [InlineKeyboardButton(text="⬅", callback_data="city_back_page"), InlineKeyboardButton(text="{0} из {1}".format(cur_page + 1, len(pages_list)), callback_data="page_info"), InlineKeyboardButton(text="➡", callback_data="city_next_page")]
            page.append(control_buttons)
            persons_keyboard = InlineKeyboardMarkup(inline_keyboard=page)

            bot.sendMessage(from_id, "Результаты по запросу:                  {}".format(query_data[11:]), reply_markup=persons_keyboard)

    elif ("profession_" in query_data):

        #global cur_page
        if (query_data[11:] != "back_page" and query_data[11:] != "next_page"):
            if (current_profession != query_data[11:]): #если текущая профессия еще не выбрана
                current_profession = query_data[11:]
                cur_page = 0 #сбрасываем страницы вывода на 1
            
        elif (query_data[11:] == "back_page"):
            cur_page = cur_page - 1
            if (cur_page < 0): cur_page = 0
        else:
            cur_page = cur_page + 1

        query = Summary.objects.filter(title=current_profession)

        #global persons_on_page  
        if not query:
            bot.sendMessage(from_id, "К сожалению ничего не найдено")
        else:
            pages_list = []
            profiles_on_page_list = []
            persons_num = 0
            for profile in query:
                if (persons_num < persons_on_page):
                    profiles_on_page_list.append([InlineKeyboardButton(text="{0} {1} \n{2}".format(profile.name, profile.second, profile.title), callback_data="person_{0}_{1}".format(profile.name, profile.second))])
                    persons_num = persons_num + 1
                else:
                    pages_list.append(profiles_on_page_list)
                    profiles_on_page_list = []
                    profiles_on_page_list.append([InlineKeyboardButton(text="{0} {1} \n{2}".format(profile.name, profile.second, profile.title), callback_data="person_{0}_{1}".format(profile.name, profile.second))])
                    persons_num = 1
            if (persons_num > 0):
                pages_list.append(profiles_on_page_list)

            page = pages_list[cur_page]
            control_buttons = [InlineKeyboardButton(text="⬅", callback_data="profession_back_page"), InlineKeyboardButton(text="{0} из {1}".format(cur_page + 1, len(pages_list)), callback_data="page_info"), InlineKeyboardButton(text="➡", callback_data="profession_next_page")]
            page.append(control_buttons)
            persons_keyboard = InlineKeyboardMarkup(inline_keyboard=page)

            bot.sendMessage(from_id, "Результаты по запросу:                  {}".format(query_data[11:]), reply_markup=persons_keyboard)

    elif ("person_" in query_data):
        person_query = Summary.objects.filter(name=query_data[7:].split('_')[0])
        person = person_query.get()
        age = round((datetime.now().date() - person.birth_date).days/365)
        bot.sendPhoto(from_id, person.img)
        bot.sendMessage(from_id, "Профиль: {0} {1} \nОписание: {2} \nВозраст: {3} \nГород: {4}".format(person.name, person.second, person.description, age, person.city))

    else:
        pass #надо что-то дописать


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print ('Chosen Inline Result:', result_id, from_id, query_string)

hook = Webhook(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result})
