#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import re
import mysql.connector
import requests
from config import *
import hashlib
import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_status_code_domain(domain_url):
    try:
        r = requests.get(domain_url, headers=useragent, allow_redirects=False, verify=False)
        status_code = r.status_code
        return status_code
    except requests.exceptions.ConnectionError:
        status_code = ''
        return status_code


def sql_select_domain(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domain_url, id FROM domains_table1 WHERE user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id, ))
        records = cursor.fetchall()
        domains_list = []
        for i in records:
            domain = i[0]
            id = i[1]
            domains_list.append(f"Домен: {domain} - ID: {id}")
        domain_str = ''
        for i in domains_list:
            domain_str += i + '\n'
        return domain_str
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def sql_insert_domain_url(domain_url, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO domains_table1 (domain_url, user_tg_id) VALUES (%s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_url, user_tg_id))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def check_domain_in_db(domain_url, user_tg_id=""):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domain_url, id FROM domains_table1 WHERE domain_url = %s AND user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_url,user_tg_id))
        records = cursor.fetchall()
        for i in records:
            url_domain = i[0]
            id = i[1]
        data_sql = {
            'id':id,
            'domain_url':url_domain
        }
        cursor.close()
        return data_sql
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        data_sql = {
            'id':"",
            'domain_url':"error"
        }
        return data_sql
    except UnboundLocalError:
        # print("Домен не найден1")
        data_sql = {
            'id':"",
            'domain_url':""
        }
        return data_sql
    finally:
        if (connection.is_connected()):
            connection.close()

def select_domain(domain_url):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domain_url, id, user_tg_id FROM domains_table1 WHERE domain_url = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_url, ))
        records = cursor.fetchall()
        for i in records:
            url_domain = i[0]
            id = i[1]
            telegram_user = i[2]
        data_sql = {
            'id':id,
            'domain_url':url_domain,
            'telegram_user':telegram_user
        }
        cursor.close()
        return data_sql
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        data_sql = {
            'id':"",
            'domain_url':"error"
        }
        return data_sql
    except UnboundLocalError:
        # print("Домен не найден1")
        data_sql = {
            'id':"",
            'domain_url':""
        }
        return data_sql
    finally:
        if (connection.is_connected()):
            connection.close()

def insert_actual_robots(domain_id, date, robots_hash, robots_encode):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO actual_robots (domain_id, date, robots_hash, robots_encode) VALUES (%s, %s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, date, robots_hash, robots_encode))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def update_actual_robots(domain_id, date, robots_hash, robots_encode):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "UPDATE actual_robots SET date = %s, robots_hash = %s, robots_encode = %s WHERE domain_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (date, robots_hash, robots_encode, domain_id))
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def delete_domain(domain_id, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "DELETE FROM domains_table1 WHERE id = %s and user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, user_tg_id))
        connection.commit()
        cursor.close()
        status = "Success"
        print(status)
        return status

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        status = "Error"
        print(status)
        return status

    finally:
        if (connection.is_connected()):
            connection.close()
def rewrite_robots_sql(domain_id, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "DELETE FROM domains_table1 WHERE id = %s and user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, user_tg_id))
        connection.commit()
        cursor.close()
        status = "Success"
        print(status)
        return status

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        status = "Error"
        print(status)
        return status

    finally:
        if (connection.is_connected()):
            connection.close()


def new_robots_txt(domain_url, domain_id):
    try:
        robots_url = domain_url + 'robots.txt'
        r = requests.get(robots_url, headers=useragent, allow_redirects=False, verify=False)
        if r.status_code == 200:
            robots_value = r.text
            if 'user-agent:' in robots_value.lower():
                hash_robots = hashlib.sha1(robots_value.encode('utf-8')).hexdigest()
                date = datetime.datetime.now()
                update_actual_robots(domain_id, date, hash_robots, robots_value)
                status = "Success"
                print(status)
                return status
            else:
                status = "Error"
                print(status + "1")
                return status

    except requests.exceptions.ConnectionError:
        robots_url = domain_url + '/robots.txt'
        r = requests.get(robots_url, headers=useragent, allow_redirects=False, verify=False)
        if r.status_code == 200:
            robots_value = r.text
            if 'user-agent:' in robots_value.lower():
                hash_robots = hashlib.sha1(robots_value.encode('utf-8')).hexdigest()
                date = datetime.datetime.now()
                insert_actual_robots(domain_id, date, hash_robots, robots_value)
                print(robots_value)
                status = "Success"
                return status
            else:
                status = "Error"
                print(status + "2")
                return status


def delete_domain_url(domain_url, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "DELETE FROM domains_table1 WHERE domain_url = %s and user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_url, user_tg_id))
        connection.commit()
        cursor.close()
        status = "Success"
        print(status)
        return status

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        status = "Error"
        print(status)
        return status

    finally:
        if (connection.is_connected()):
            connection.close()


def get_slash_domain(url_domain):
    result = re.findall(r'\/', url_domain)
    print(url_domain)
    print(result)
    print(len(result))
    if len(result) == 2:
        print("Закрывающего слеша нет на конце")
        slash = "slash_not_ok"
        return slash
    elif len(result) == 3:
        print("Есть закрывающий слеш на конце")
        slash = "slash_ok"
        return slash
    else:
        print("Вы прислали не главную страницу.")
        slash = "Error"
        return slash


def check_robotstxt(domain_url, domain_id):
    try:
        slash = get_slash_domain(domain_url)
        if slash == "slash_ok":
            robots_url = domain_url + 'robots.txt'
            r = requests.get(robots_url, headers=useragent, allow_redirects=False, verify=False)
            if r.status_code == 200:
                robots_value = r.text
                if 'user-agent:' in robots_value.lower():
                    hash_robots = hashlib.sha1(robots_value.encode('utf-8')).hexdigest()
                    date = datetime.datetime.now()
                    insert_actual_robots(domain_id, date, hash_robots, robots_value)
                    status = "Success"
                    return status
                else:
                    status = "Error"
                    return status
        elif slash == "slash_not_ok":
            print(slash)
            robots_url = domain_url + '/robots.txt'
            r = requests.get(robots_url, headers=useragent, allow_redirects=False, verify=False)
            if r.status_code == 200:
                robots_value = r.text
                if 'user-agent:' in robots_value.lower():
                    hash_robots = hashlib.sha1(robots_value.encode('utf-8')).hexdigest()
                    date = datetime.datetime.now()
                    insert_actual_robots(domain_id, date, hash_robots, robots_value)
                    print(robots_value)
                    status = "Success"
                    return status
                else:
                    status = "Error"
                    return status
        elif slash == "Error":
            status = "Error"
            return status

    except requests.exceptions.ConnectionError:
            status = "Error"
            return status


"""Функция добавляет домен в БД"""
def domain_url_add_to_bd(domain_url, user_tg_id):
    response_code_domain = check_status_code_domain(domain_url)
    if response_code_domain == 200:
        domain = check_domain_in_db(domain_url, user_tg_id)
        if domain['domain_url'] != domain_url:
            sql_insert_domain_url(domain_url, user_tg_id)
            domain = check_domain_in_db(domain_url, user_tg_id)
            if domain['domain_url'] == domain_url:
                status_robots_txt = check_robotstxt(domain['domain_url'], domain['id'])
                if status_robots_txt == "Success":
                    result = "Success"
                    # print(result)
                    return result
                else:
                    result = "Error0"
                    # print("Сервер распознал бота. Скорректируйте работу своего сервера или не добавляйте этот домен.")
                    return result
        else:
            result = "Error1"
            return result
    else:
        result = "Error2"
        # print("Ошибка добавления. Вы прислали некорректный домен. (код ответа сервера НЕ 200 ОК)")
        return result


def check_domain_id_and_tg_id(id_domain, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domain_url FROM domains_table1 WHERE id = %s AND user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (id_domain, user_tg_id))
        records = cursor.fetchall()
        data_list = []
        for i in records:
            url_domain = i[0]
            data_list = url_domain
        cursor.close()
        return data_list
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        data_list = ''
        return data_list
    except UnboundLocalError:
        print("Домен не найден")
        data_list = ''
        return data_list
    finally:
        if (connection.is_connected()):
            connection.close()


def days_expired(domain_name, dict_time):
    dict_result_expired = {}
    expired_date = dict_time.date() #Дата освобождения
    datetime_now = datetime.datetime.now()
    difference = dict_time - datetime_now
    difference_days = difference.days #сколько дней осталось до освобождени
    dict_result_expired['expired_date'] = expired_date
    dict_result_expired['difference_days'] = difference_days
    dict_result_expired['domain_name'] = domain_name
    return dict_result_expired


def request_api_xml(domain_name):
    url_api = 'https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey='
    final_url = url_api + apiKey + '&domainName=' + domain_name + '&outputFormat=JSON'
    dict_result = requests.get(final_url).json()
    date_expired = dict_result['WhoisRecord']['registryData']['expiresDate']
    time_for_bd = datetime.datetime.strptime(date_expired, "%Y-%m-%dT%H:%M:%SZ")
    dict_expired = days_expired(domain_name, time_for_bd)
    return dict_expired

def sql_insert_expired(domain_id, date_expired, difference_days):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO expired(domain_id, date_expired, difference_days) VALUES(%s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id, date_expired, difference_days))
        connection.commit()
        cursor.close()
        status = "Success"
        print(status)
        return status

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
        status = "Error"
        print(status)
        return status

    finally:
        if (connection.is_connected()):
            connection.close()
#