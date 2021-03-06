#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import logging
from datetime import time
import os
import subprocess
import time
import config
import telebot
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from telebot import types
from actions_with_domain import domain_url_add_to_bd, \
    sql_select_domain, \
    delete_domain, \
    check_domain_id_and_tg_id, \
    delete_domain_url, new_robots_txt, request_api_xml, sql_insert_expired, select_domain

from profile_sql import get_col_domains_from_user, \
    get_uptime_for_user, \
    get_date_and_domain_expired, \
    correctly_telephone, insert_telephone, get_telephone, get_file_expired, \
    get_information_speed_response_txt_check_from_sql, get_information_robots_txt_check_from_sql, \
    update_mobile_operator, select_interval_notification, update_interval_notification

list_domains = ""

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def get_text_messages(message):
    print(message.from_user.id)
    print(message.text)
    start_menu = types.ReplyKeyboardMarkup(True, True)
    start_menu.row('✅️Добавить сайт', '❌ Удалить сайт')
    start_menu.row('🖊️ Перезаписать HASH robots', '👀 Мой профиль')
    start_menu.row('📈 Получить логи проверок')
    bot.send_message(message.chat.id, 'Стартовое меню', reply_markup=start_menu)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    if message.text == '✅️Добавить сайт':
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        print(message.chat.id)
        print(message.text)
        bot.send_message(message.chat.id,
                         f"1️⃣ Пришлите мне адрес домена, который требуется отслеживать.\n"
                         f"2️⃣ Я добавлю домен в вашу базу данных и буду проверять его каждые 10 минут.\n"
                         f"3️⃣ Мною отслеживаются параметры:\n"
                         f"✔️код ответа сервера;\n"
                         f"✔️изменения в файле robots.txt;\n"
                         f"✔️дата освобождения;\n"
                         f"⚠️Если кто-то изменит robots.txt или домен будет недоступен, вы получите уведомление.\n"
                         f"Примеры добавления домена:\n"
                         f"https://site.ru\n"
                         f"http://site.ru\n"
                         f"https://www.site.ru",
                         reply_markup=back_button, parse_mode="HTML")
        bot.register_next_step_handler(message, add_site_bd)

    elif message.text == '❌ Удалить сайт':
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        print(message.chat.id)
        print(message.text)
        domain_list = sql_select_domain(user_id)
        if len(domain_list) >= 1:
            bot.send_message(message.chat.id, text=
            f"Для <b>удаления</b> сайта требуется указать его <b>ID</b> из указанного ниже списка.\n"
            f"👇Ваш список отслеживаемых доменов:👇\n"
            f"{domain_list}\n"
            f"Укажите ID выбранного домена для удаления", parse_mode="HTML",
                             reply_markup=back_button)
            bot.register_next_step_handler(message, delete_site_bd)
        else:
            bot.send_message(message.chat.id, f"Ваш список отслеживаемых доменов пуст 😟\n"
                                              f"Для продолжения напишите /start и добавьте новый домен.")

    elif message.text == '🖊️ Перезаписать HASH robots':
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        print(message.chat.id)
        print(message.text)
        domain_list = sql_select_domain(user_id)
        if len(domain_list) >= 1:
            bot.send_message(message.chat.id, f"Ваш список отслеживаемых доменов:\n{domain_list}"
                                              f"\nУкажите ID выбранного домена для перезаписи robots",
                             reply_markup=back_button)
            bot.register_next_step_handler(message, rewrite_robots_hash)
        else:
            bot.send_message(message.chat.id, f"Ваш список отслеживаемых доменов пуст 😟\n"
                                              f"Для продолжения напишите /start и добавьте новый домен.")

    if message.text == '👀 Мой профиль':
        back_button = types.ReplyKeyboardMarkup(True, True)
        actual_telephone_user = get_telephone(message.chat.id)
        if len(actual_telephone_user) == 0:
            back_button.row('Добавить номер телефона (только РФ)')
        back_button.row('Обратная связь')
        back_button.row('Изменить интервал уведомлений')
        back_button.row('Назад')
        print(message.chat.id)
        print(message.text)
        col = get_col_domains_from_user(message.chat.id)
        if col == 0:
            uptime = "Недостаточно данных"
        else:
            uptime = get_uptime_for_user(message.chat.id)
        expired_domain_result_from_user = get_date_and_domain_expired(message.chat.id)
        if int(len(expired_domain_result_from_user)) >= 1:
            domain_name = expired_domain_result_from_user['domain_url']
            date_expired_domain = expired_domain_result_from_user['date_expired']
            difference_days = expired_domain_result_from_user['difference_days']
        else:
            domain_name = "Неизвестно"
            date_expired_domain = "Неизвестно"
            difference_days = "Неизвестно"
        if len(actual_telephone_user) == 0:
            actual_telephone_user = 'Неизвестен'
        bot.send_message(message.chat.id,
                         f"👮 Количество отслеживаемых доменов, шт.: {col}\n"
                         f"🕒 Средний UPTIME по всем доменам: {uptime}\n"
                         f"🌐 Ближайший освобождающийся домен: {domain_name}\n"
                         f"📅 Дата освобождения: {date_expired_domain}\n"
                         f"📅 Дней до освобождения: {difference_days}\n"
                         f"⌛ Интервал проверки доменов, минут: 10\n"
                         f"☎️Ваш номер телефона для SMS-уведомлений: {actual_telephone_user}\n",
                         reply_markup=back_button)
        # bot.register_next_step_handler(message, add_site_bd)
    elif message.text == 'Обратная связь':
        print(message.chat.id)
        print(message.text)
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        bot.send_message(message.chat.id, f"Если у вас возник вопрос "
                                          f"или вы заметили ошибку в работе бота, отправьте нам сообщение. "
                                          f"Мы рассмотрим ваше обращение в течение 24 часов.\n"
                                          f"Формат обращения👇\n"
                                          f"<b>1️⃣ Ваше имя:</b>\n"
                                          f"<b>2️⃣ Описание ошибки или жалоба:</b>",
                         reply_markup=back_button, parse_mode="HTML")
        # bot.register_next_step_handler(message, add_site_bd)
    elif message.text == 'Добавить номер телефона (только РФ)':
        print(message.chat.id)
        print(message.text)
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        bot.send_message(message.chat.id, f"Пришлите мне номер телефона в формате <b>7XXXXXXXXXX</b>\n"
                                          f"📱 Пример номера: <b>79647489485</b>\n"
                                          f"Требуемая длина номера: 11 символов\n"
                                          f"Номер должен начинаться с <b>7</b>\n"
                                          f"✉️ На указанный номер будут поступать SMS-уведомления о доступности сайтов.",
                         reply_markup=back_button, parse_mode="HTML")
        bot.register_next_step_handler(message, add_telephone)
    elif message.text == 'Изменить интервал уведомлений':
        print(message.chat.id)
        print(message.text)
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        bot.send_message(message.chat.id, f"Стандартный интервал уведомлений в случае ошибок: <b>600</b> секунд.\n"
                                          f"Если вы получаете уведомления часто, укажите требуемый интервал.\n"
                                          f"👇<b>Пришлите мне целое число (секунды)</b>👇\n",
                         reply_markup=back_button, parse_mode="HTML")
        bot.register_next_step_handler(message, add_seconds_timedelta)

    elif message.text == 'Назад':
        print(message.text)
        get_text_messages(message)

    if message.text == '📈 Получить логи проверок':
        print("Logs")
        user_id = message.from_user.id
        print(user_id)
        back_button = types.ReplyKeyboardMarkup(True, True)
        back_button.row('Назад')
        bot.send_message(message.chat.id, f"⌛ Подготавливаю файлы. Пожалуйста, ожидайте.",
                             reply_markup=back_button)
        robots = get_information_robots_txt_check_from_sql(user_id)
        print(robots)
        speed = get_information_speed_response_txt_check_from_sql(user_id)
        print(speed)
        expired = get_file_expired(user_id)
        print(expired)
        try:
            robots_open = open(robots, 'rb')
            speed_open = open(speed, 'rb')
            expired_open = open(expired, 'rb')
            bot.send_document(message.chat.id, robots_open)
            bot.send_document(message.chat.id, speed_open)
            bot.send_document(message.chat.id, expired_open)
            robots_open.close()
            speed_open.close()
            expired_open.close()
            bot.send_message(message.chat.id, f"🔥 Файлы готовы. Для продолжения нажмите 'Назад' или /start",
                                 reply_markup=back_button)
        except FileNotFoundError:
            bot.send_message(message.chat.id, f"⚠️ Ваша база данных пуста. Для продолжения нажмите 'Назад' или /start",
                                 reply_markup=back_button)

def add_seconds_timedelta(message):
    if message.text == 'Назад':
        get_text_messages(message)
    else:
        try:
            user_id = message.from_user.id
            select_interval_notification(user_id)
            seconds = int(message.text)
            update_interval_notification(user_id, seconds)
            print(seconds)
            bot.send_message(message.chat.id, f"✅ Интервал уведомлений успешно изменен.\n"
                                              f"Для продолжения нажмите 'Назад' или /start")
        except ValueError:
            bot.send_message(message.chat.id, f"Вы указали некорректное число. "
                                              f"Для продолжения нажмите 'Назад' или /start")


def add_site_bd(message):
    try:

        if message.text == 'Назад':
            get_text_messages(message)
        else:
            user_id = message.from_user.id
            print(message.from_user.username)
            domain_name_telegram = message.text
            domain_name_telegram = str(domain_name_telegram).lower()
            print(domain_name_telegram)
            print(f"USER ID: {user_id} пытается добавить домен {domain_name_telegram}")
            status = domain_url_add_to_bd(domain_name_telegram, user_id)
            print(status)
            if status == 'Success':
                expired = request_api_xml(domain_name_telegram)
                expired_days = expired['difference_days']
                expired_date = expired['expired_date']
                domain = select_domain(domain_name_telegram)
                domain_id = domain['id']
                sql_insert_expired(domain_id, expired_date, expired_days)
                print(f"Домен {domain_name_telegram} успешно добавлен в базу данных пользователя {user_id}")
                bot.send_message(message.from_user.id,
                                 f"🌐 Домен: {domain_name_telegram}\n"
                                 f"✅ Успешно добавлен в базу данных пользователя: {user_id}\n"
                                 f"📅 Количество дней до освобождения домена: {expired_days}\n"
                                 f"Для продолжения напишите /start или нажмите на кнопку 'Назад'")
            elif status == "Error1":
                bot.send_message(message.from_user.id,
                                 f"⚠ Домен {domain_name_telegram} ранее был добавлен в базу данных.\n"
                                 f"Для продолжения напишите /start")
            elif status == "Error2":
                bot.send_message(message.from_user.id,
                                 f"❌ Код ответа сервера для домена НЕ равен 200 ОК.\n"
                                 f"⚠️Проверьте корректность написания доменного имени и его протокола.\n"
                                 f"Для продолжения напишите /start")
            elif status == "Error0":
                delete_domain_url(domain_name_telegram, user_id)
                bot.send_message(message.from_user.id,
                                 f"❌ Ошибка добавления. Ваш сервер заблокировал нашего бота или вы прислали "
                                 f"некорректный домен.\n Скорректируйте работу своего сервера или не добавляйте этот "
                                 f"домен.\n "
                                 f"Для продолжения напишите /start")
            else:
                bot.send_message(message.from_user.id, f"Неизвестная ошибка. Напишите /start")
    except ValueError:
        bot.send_message(message.from_user.id, f"Ошибка добавления домена. Напишите /start")
    except TypeError:
        bot.send_message(message.from_user.id, f"Ошибка добавления домена. Напишите /start")


def delete_site_bd(message):
    try:
        if message.text == 'Назад':
            get_text_messages(message)
        else:
            domain_id = message.text
            user_id = message.from_user.id
            print(f"Пользователь {user_id} отправил заявку на удаление домена {domain_id} из БД")
            len_list_domain = check_domain_id_and_tg_id(domain_id, user_id)
            if int(len(len_list_domain)) >= 1:
                delete = delete_domain(domain_id, user_id)
                if delete == "Success":
                    bot.send_message(message.from_user.id, f"Домен ID {domain_id} удален из БД. Продолжить /start")
            else:
                bot.send_message(message.from_user.id, f"Указан некорректный id. Напишите /start и повторите команду")
    except ValueError:
        bot.send_message(message.from_user.id, f"Указан некорректный id. Напишите /start и повторите команду")


def rewrite_robots_hash(message):
    try:
        if message.text == 'Назад':
            get_text_messages(message)
        else:
            domain_id = message.text
            user_id = message.from_user.id
            print(f"Пользователь {user_id} отправил заявку на перезапись robots.txt для домена {domain_id}")
            len_list_domain = check_domain_id_and_tg_id(domain_id, user_id)
            len_list = len(len_list_domain)
            if len_list >= 1:
                print(len_list_domain)
                new_robots = new_robots_txt(len_list_domain, domain_id)
                if new_robots == 'Success':
                    print(f"ROBOTS.TXT для домена: {len_list_domain} успешно перезаписан.")
                    bot.send_message(message.from_user.id,
                                     f"ROBOTS.TXT для домена: {len_list_domain} успешно перезаписан.")
            else:
                bot.send_message(message.from_user.id, f"Указан некорректный id. Напишите /start и повторите команду")
    except ValueError:
        bot.send_message(message.from_user.id, f"Указан некорректный id. Напишите /start и повторите команду")

def add_telephone(message):
    try:
        if message.text == 'Назад':
            get_text_messages(message)
        else:
            user_id = message.from_user.id
            print(f"Пользователь {user_id} пытается добавить номер телефона")
            status_number = correctly_telephone(message.text)
            print(status_number)
            if status_number == 'Error':
                bot.send_message(message.from_user.id, f"Указан некорректный номер телефона.\n"
                                                       f"Напишите /start и повторите команду")
            elif status_number == 'Success':
                telephone = message.text
                print(telephone)
                bot.send_message(message.from_user.id, f"Ваш оператор:\n"
                                                       f"/Tele2\n"
                                                       f"\n"
                                                       f"/MTS\n"
                                                       f"\n"
                                                       f"/Yota\n"
                                                       f"\n"
                                                       f"/Megafon\n"
                                                       f"\n"
                                                       f"/Beeline")
                insert_telephone(message.text, user_id)
                bot.register_next_step_handler(message, id_operator)

    except ValueError:
        bot.send_message(message.from_user.id, f"Указан некорректный номер. Напишите /start и повторите команду")


def id_operator(message):
    try:
        if message.text == 'Назад':
            get_text_messages(message)
        else:
            user_id = message.from_user.id
            if message.text == '/Tele2':
                update_mobile_operator(user_id, "Tele2")
                bot.send_message(message.from_user.id, f"Добавление номера завершено. Для продолжения напишите /start")
            elif message.text == '/MTS':
                update_mobile_operator(user_id, "MTS")
                bot.send_message(message.from_user.id, f"Рассылка на MTS невозможна. Для продолжения напишите /start и"
                                                       f" добавьте номер другого оператора.")
            elif message.text == '/Yota':
                update_mobile_operator(user_id, "Yota")
                bot.send_message(message.from_user.id, f"Добавление номера завершено. Для продолжения напишите /start")
            elif message.text == '/Megafon':
                update_mobile_operator(user_id, "Megafon")
                bot.send_message(message.from_user.id, f"Добавление номера завершено. Для продолжения напишите /start")
            elif message.text == '/Beeline':
                update_mobile_operator(user_id, "Beeline")
                bot.send_message(message.from_user.id, f"Добавление номера завершено. Для продолжения напишите /start")
            else:
                print("Ошибка указания оператора")
                bot.send_message(message.from_user.id, f"Указан некорректный моб. оператор. "
                                                       f"Напишите /start и повторите команду")

    except ValueError:
        bot.send_message(message.from_user.id, f"Указан некорректный id. Напишите /start и повторите команду")

def main():
    com = 'pgrep -f telegram_bot.py'
    p = subprocess.Popen([com], stdout=subprocess.PIPE, shell=True)
    res = p.communicate()[0]
    if isinstance(res, bytes):
        res = res.decode("utf-8")
    res = [str(x) for x in res.split('\n') if len(x) > 0]
    print('Ожидаем 10 секунд')
    time.sleep(10)
    if len(res) >= 3:
        print(len(res))
        print('Процесс запущен. Запуск не требуется.')
    else:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as err:
            logging.error(err)
            time.sleep(5)
            print("Internet error!")

if __name__ == '__main__':
    main()

#
