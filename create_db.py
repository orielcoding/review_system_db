import mysql.connector
import json


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    connection = mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    cursor = connection.cursor()

    # create table reviews, with generated incrementing id
    cursor.execute("""CREATE TABLE reviews (to fill)""")  # with foreign key to products and stores

    cursor.execute("""CREATE TABLE stores (to fill)""")  # store_id, store_name, organization token

    cursor.execute("""CREATE TABLE stores_reviews (to fill)""")  # foreign key to reviews and stores

    cursor.execute("""CREATE TABLE syndication (to fill)""")  # source_store_id, target_store_id
