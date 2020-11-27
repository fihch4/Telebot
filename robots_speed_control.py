#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import requests
import mysql.connector
from config import *
import datetime
import hashlib
from actions_with_domain import select_domain, get_slash_domain
import urllib3
from multiprocessing import Pool
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import telebot
bot = telebot.TeleBot(token)


def domain_list():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domain_url from domains_table1"
        cursor = connection.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        domain_list= []
        for i in records:
            domain_list.append(i[0])
        cursor.close()
        return domain_list
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    except UnboundLocalError:
        print("Ошибка формирования списка доменов")
    finally:
        if (connection.is_connected()):
            connection.close()


def insert_sql_speed(domain_id, date, response_speed):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO actual_speed_server (domain_id, date, speed_response) VALUES (%s, %s, %s)"

        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, date, response_speed))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()

def insert_sql_robots_hash_each(domain_id, date, robots_hash, robots_encode):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO robots_txt_each_check (domain_id, date, robots_hash, robots_encode) VALUES (%s, %s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, date, robots_hash, robots_encode))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def check_old_robots(domain_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT robots_hash from actual_robots WHERE domain_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, ))
        records = cursor.fetchall()
        for i in records:
            old_robots = i[0]
        cursor.close()
        return old_robots
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def insert_status_log_verification(domain_id, status, verification_value):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO log_verification(domain_id, status, verification_value, date) VALUES(%s, %s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, status, verification_value, datetime.datetime.now()))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()
def get_status_code_domain(domain_url):
    try:
        status_code = ""
        while status_code != 200:
            r = requests.get(domain_url, headers=useragent, allow_redirects=False, verify=False)
            status_code = r.status_code
            return status_code
    except requests.exceptions.ConnectionError:
        status_code = "Error"
        return status_code

def check_final_status_code(domain_url, domain_id, telegram_user_id):
    try:
        print(domain_url)
        status_code = ""
        num_cycle = 0
        while status_code != 200:
            status_code = get_status_code_domain(domain_url)
            if num_cycle >= 1:
                print("Пауза на текущий поток, так как домен недоступен")
                time.sleep(pause_sleep)
                if num_cycle >= num_max_check:
                    break
            num_cycle += 1
        if status_code == 200:
            insert_status_log_verification(domain_id, "Success", "Response Code")
            status = "Success"

            time.sleep(5)
            return status
        else:
            timeout_waiting_status_code = num_max_check * pause_sleep
            insert_status_log_verification(domain_id, "Error", "Response Code")
            print("Домен: " + str(domain_url) + " НЕДОСТУПЕН. Надо отправить уведомление.")
            bot.send_message(chat_id=telegram_user_id, text=f"❗Внимание❗\n"
                                                            f"Домен: {domain_url} недоступен после {num_max_check}"
                                                            f"повторных проверок. "
                                                            f"Общее время ожидания доступности домена составляет: "
                                                            f"{timeout_waiting_status_code} секунд.")
            status = "Error"
            return status
    except requests.exceptions.ConnectionError:
        status = "Error"
        return status

def check_robotstxt_for_each_table(domain_url, domain_id, telegram_user_id):
    try:
        slash = get_slash_domain(domain_url)
        if slash == "slash_ok":
            robots_url = domain_url + 'robots.txt'
        elif slash == "slash_not_ok":
            robots_url = domain_url + '/robots.txt'
        elif slash == "Error":
            print("Ошибка определения количества слешей для robots.txt")

        status_code = check_final_status_code(domain_url, domain_id, telegram_user_id)
        if status_code == "Success":
            response_speed(domain_url)
            r = requests.get(robots_url, headers=useragent, allow_redirects=False, verify=False)
            status_code = r.status_code
            print(status_code)
            if r.status_code == 200:
                robots_value = r.text
                hash_robots = hashlib.sha1(robots_value.encode('utf-8')).hexdigest()
                date = datetime.datetime.now()
                insert_sql_robots_hash_each(domain_id, date, hash_robots, robots_value)
                robots_old = check_old_robots(domain_id)
                if robots_old != hash_robots:
                    print("ROBOTS не СОВПАЛИ. СЮДА ДОБАВИТЬ ОТПРАВКУ УВЕДОМЛЕНИЯ В ТЕЛЕГУ И В СМС")
                    insert_status_log_verification(domain_id, "Rewrite", "Robots")
                    print("Домен: " + str(domain_url) + " Изменен robots.txt")
                    bot.send_message(chat_id=telegram_user_id, text=f"❗Внимание❗\n"
                                                                    f"Был изменен файл robots.txt "
                                                                    f"для домена {domain_url}.\n"
                                                                    f"Если вы намеренно изменили robots.txt, "
                                                                    f"рекомендуем перезаписать его HASH, чтобы "
                                                                    f"не получать уведомления до следующего изменения.")
                    status = "Robots Rewrite"
                    return status
                elif robots_old == hash_robots:
                    status = "Robots Success"
                    insert_status_log_verification(domain_id, "Success", "Robots")
                    return status
    except requests.exceptions.ConnectionError:
        status = "Robots Error"
        insert_status_log_verification(domain_id, "Error", "Robots")
        return status


def response_speed(domain_url):
    try:
        r = requests.get(domain_url, headers=useragent, allow_redirects=False, verify=False)
        status_code = r.status_code
        domain = select_domain(domain_url)
        domain_id = domain['id']
        if status_code == 200:
            dict_speed = {}
            r_speed = r.elapsed.total_seconds()
            dict_speed['speed'] = r_speed
            dict_speed['status'] = 'Success'
            date = datetime.datetime.now()
            insert_sql_speed(domain_id, date, dict_speed['speed'])
            insert_status_log_verification(domain_id, "Success", "Speed")
            time.sleep(5)
            return dict_speed
        else:
            dict_speed = {}
            dict_speed['status'] = 'Error'
            insert_status_log_verification(domain_id, "Error", "Speed")
            return dict_speed
    except requests.exceptions.ConnectionError:
        dict_speed = {}
        dict_speed['status'] = 'Error'
        insert_status_log_verification(domain_id, "Error", "Speed")
        return dict_speed


def speed_server_and_robots_hash(domain_url):
    print(domain_url)
    domain = select_domain(domain_url)
    print(domain)
    domain_id = domain['id']
    telegram_id = domain['telegram_user']
    check_robotstxt_for_each_table(domain_url, domain_id, telegram_id)


def main():
    domains = domain_list()
    threads = len(domains) // 2
    if threads >= 15:
        threads = 10
    elif threads <= 0:
        threads = 1
    with Pool(threads) as p:
        p.map(speed_server_and_robots_hash, domains)

if __name__ == '__main__':
    main()
#