#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import mysql.connector
from config import *
import datetime
from actions_with_domain import request_api_xml
import telebot
bot = telebot.TeleBot(token)

def get_dictionary_domains_expired():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "SELECT domains_table1.domain_url, domains_table1.id, domains_table1.user_tg_id, expired.date_expired " \
              "FROM domains_table1 INNER JOIN" \
              " expired ON expired.domain_id = domains_table1.id;"
        cursor = connection.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        domains_dictionary = {}
        for record in records:
            domains_dictionary[record[0]] = {'id':record[1],'user_tg_id':record[2], 'date_expired':record[3]}
        cursor.close()
        return domains_dictionary
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))
    finally:
        if (connection.is_connected()):
            connection.close()


def update_difference_days(domain_id, difference_days):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_home
        )
        sql = "UPDATE expired SET difference_days = %s WHERE domain_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (difference_days, domain_id))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()


def get_difference_days_expired(date_expired):
    date_now = datetime.datetime.now()
    difference_date = date_expired - date_now
    return difference_date.days


def main():
    dictionary = (get_dictionary_domains_expired())
    for domain in dictionary:
        domain_name = domain
        domain_date_expired = dictionary[domain]['date_expired']
        domain_id = dictionary[domain]['id']
        user_tg_id = dictionary[domain]['user_tg_id']
        days_expired = get_difference_days_expired(domain_date_expired)
        print(days_expired)
        update_difference_days(domain_id, days_expired)
        if days_expired <= days_expired_check:
            expired_actual_check = request_api_xml(domain_name)
            date_now = expired_actual_check['expired_date']
            if domain_date_expired.date() == date_now:
                print("Дата освобождения домена еще не обновлена. Запись в БД новой даты не требуется")
                bot.send_message(chat_id=user_tg_id, text=f"❗Внимание❗\n"
                                                                f"Домен: {domain_name} освобождается {date_now}\n"
                                                          f"Дней до освобождения домена: {days_expired}\n"
                                                          f"Срочно продлите домен.")
            else:
                print("Дата освобождения домена обновлена. Перезаписываем информацию в БД.")


if __name__ == '__main__':
    main()

#