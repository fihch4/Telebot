#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import os
import time
import json
from random import randint
import requests
import mysql.connector
from config import *
import re
import csv


def get_col_domains_from_user(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT COUNT(domain_url) FROM domains_table1 WHERE user_tg_id=%s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        for i in records:
            col_domains_from_user = i[0]
        cursor.close()
        return col_domains_from_user
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def get_previous_date_notification_user(domain_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "select date from log_verification where status = 'Error' and domain_id = %s order by date desc limit 1"
        cursor = connection.cursor()
        cursor.execute(sql, (domain_id,))
        records = cursor.fetchall()
        for i in records:
            previous_date = i[0]
        cursor.close()
        return previous_date
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def get_telephone(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT telephone FROM users WHERE user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        for i in records:
            telephone_number = i[0]
        cursor.close()
        return telephone_number
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    except UnboundLocalError:
        telephone_number = ''
        return telephone_number
    finally:
        if (connection.is_connected()):
            connection.close()


def insert_telephone(telephone_number, user_tg_id, mobile_operator="Null"):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO users (telephone, user_tg_id, mobile_operator) VALUES (%s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (telephone_number, user_tg_id, mobile_operator))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def insert_interval_notification(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO interval_notification_users (interval_notification, user_tg_id) VALUES (%s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, ("600", user_tg_id ))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def select_interval_notification(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT interval_notification FROM interval_notification_users WHERE user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id, ))
        records = cursor.fetchall()
        for i in records:
            interval_notification = i[0]
        cursor.close()
        return interval_notification
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    except UnboundLocalError:
        insert_interval_notification(user_tg_id)
        interval_notification = "600"
        return interval_notification
    finally:
        if (connection.is_connected()):
            connection.close()


def update_interval_notification(user_tg_id, interval_notification):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "UPDATE interval_notification_users SET interval_notification = %s WHERE user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (interval_notification, user_tg_id, ))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def get_num_errors_response_code(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT count(log_verification.status) " \
              "FROM log_verification INNER JOIN domains_table1 " \
              "ON domains_table1.id = log_verification.domain_id " \
              "WHERE log_verification.verification_value='Response Code' " \
              "and domains_table1.user_tg_id = %s and log_verification.status='Error'"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        for i in records:
            count_errors_response_code = int(i[0])
        cursor.close()
        return count_errors_response_code

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def get_uptime_for_user(user_tg_id):
    num_errors = get_num_errors_response_code(user_tg_id)
    dict_uptime = {
        "tier_one": {"99.671": "1728"},
        "tier_two": {"99.741": "1320"},
        "tier_three": {"99.982": "96"},
        "tier_four": {"99.995": "24"}
    }

    if num_errors <= float(dict_uptime['tier_one']["99.671"]):
        uptime = "99.671"
        if num_errors <= float(dict_uptime['tier_two']["99.741"]):
            uptime = "99.741"
            if num_errors <= float(dict_uptime['tier_three']["99.982"]):
                uptime = "99.982"
                if num_errors <= float(dict_uptime['tier_four']["99.995"]):
                    uptime = "99.995"
    return uptime


def get_date_and_domain_expired(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domains_table1.domain_url, " \
              "domains_table1.id, domains_table1.user_tg_id, expired.date_expired, expired.difference_days FROM " \
              "domains_table1 INNER JOIN expired ON expired.domain_id = domains_table1.id " \
              "WHERE user_tg_id = %s ORDER BY difference_days DESC LIMIT 1;"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        next_expired_domain_and_date = {}
        for i in records:
            next_expired_domain_and_date['domain_url'] = i[0]
            next_expired_domain_and_date['user_tg_id'] = i[2]
            next_expired_domain_and_date['date_expired'] = i[3]
            next_expired_domain_and_date['difference_days'] = i[4]
        cursor.close()
        return next_expired_domain_and_date

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def correctly_telephone(telephone_from_user):
    check_seven_in_number = seven_correctly_telephone(telephone_from_user)
    if len(telephone_from_user) == 11:
        if check_seven_in_number == 'Success':
            result = 'Success'
            return result
    else:
        print("Вы прислали некорректный номер телефона.")
        print("Общее количество цифр должно быть равно 11")
        result = 'Error'
        return result


def seven_correctly_telephone(telephone_from_user):
    result = re.findall(r'^7', telephone_from_user)
    if '7' in result:
        result = 'Success'
        return result
    else:
        result = 'Error'
        return result


def generate_filename_robots_txt(user_tg_id):
    random_number = randint(0, 50)
    final_file_name = 'robots_' + str(user_tg_id) + str(random_number) + '.csv'
    return final_file_name


def get_information_robots_txt_check_from_sql(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "select distinct robots_txt_each_check.robots_encode, domains_table1.domain_url from robots_txt_each_check inner join " \
              "domains_table1 on domains_table1.id = robots_txt_each_check.domain_id where " \
              "domains_table1.user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        file_name = generate_filename_robots_txt(user_tg_id)
        for i in records:
            dict = {}
            robots_txt = i[0].replace('\r', '')
            domain_url = i[1]
            dict[domain_url] = robots_txt
            with open(file_name, mode="a", encoding='utf-8') as w_file:
                file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
                file_writer.writerow([dict])
        cursor.close()
        return file_name
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def generate_filename_speed_txt(user_tg_id):
    random_number = randint(0, 50)
    final_file_name = 'speed_' + str(user_tg_id) + str(random_number) + '.csv'
    return final_file_name

def get_information_speed_response_txt_check_from_sql(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "select domains_table1.domain_url, actual_speed_server.speed_response, " \
              "actual_speed_server.date from actual_speed_server inner join domains_table1 " \
              "on domains_table1.id = actual_speed_server.domain_id " \
              "where domains_table1.user_tg_id = %s " \
              "order by actual_speed_server.date desc"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        file_name = generate_filename_speed_txt(user_tg_id)
        for i in records:
            list_speed = []
            domain = i[0]
            speed = i[1]
            date = i[2]
            list_speed.append(f"{domain};{speed};{date}")
            with open(file_name, mode="a", encoding='utf-8') as w_file:
                file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
                file_writer.writerow([list_speed[0]])
        cursor.close()
        return file_name
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def generate_filename_expired_txt(user_tg_id):
    random_number = randint(0, 50)
    final_file_name = 'expired_' + str(user_tg_id) + str(random_number) + '.csv'
    return final_file_name


def get_file_expired(user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "select domains_table1.domain_url, expired.date_expired from expired " \
              "inner join domains_table1 on domains_table1.id = expired.domain_id " \
              "where domains_table1.user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (user_tg_id,))
        records = cursor.fetchall()
        file_name = generate_filename_expired_txt(user_tg_id)
        for i in records:
            list_expired = []
            domain = i[0]
            date_expired = i[1]
            list_expired.append(f"{domain};{date_expired}")
            with open(file_name, mode="a", encoding='utf-8') as w_file:
                file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
                file_writer.writerow([list_expired[0]])
        cursor.close()
        return file_name
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()

def delete_files(file_path):
    try:
        os.remove(file_path)
        return "Success"
    except PermissionError:
        return "Error"

def update_mobile_operator(user_tg_id, mobile_operator):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "UPDATE users SET mobile_operator = %s WHERE user_tg_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (mobile_operator, user_tg_id))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()

#
