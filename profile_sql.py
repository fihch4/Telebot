#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import mysql.connector
from config import *
import re

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
        cursor.execute(sql, (user_tg_id, ))
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
        cursor.execute(sql, (user_tg_id, ))
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


def insert_telephone(telephone_number, user_tg_id):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "INSERT INTO users (telephone, user_tg_id) VALUES (%s, %s)"
        cursor = connection.cursor()
        cursor.execute(sql, (telephone_number, user_tg_id))
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
        "tier_one":{"99.671":"1728"},
        "tier_two":{"99.741":"1320"},
        "tier_three":{"99.982":"96"},
        "tier_four":{"99.995":"24"}
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

#