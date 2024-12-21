import json
import mysql.connector

with open('config.json') as f:
    config = json.load(f)

connection = mysql.connector.connect(  # TODO: separate concerns - all db actions in db_interactions.py
    host=config['host'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)
cursor = connection.cursor()


def add_row_reviews(request):
    cursor.execute("""
    INSERT INTO reviews (review_content, review_rating, store_id, product_id, request_time)
    VALUES (%s, %s, %s, %s, %s)
    """, request)


def update_reviews_table(request_time, review_content, review_id, review_rating):
    cursor.execute("""
    UPDATE reviews
    SET review_content = %s, review_rating = %s, request_time = %s
    WHERE review_id = %s
    """, (review_content, review_rating, request_time, review_id))


def delete_from_stores_reviews(review_id):
    cursor.execute("""
    DELETE FROM stores_reviews
    WHERE review_id = %s
    """, (review_id,))


def delete_from_reviews(review_id):
    cursor.execute("""
    DELETE FROM reviews
    WHERE review_id = %s
    """, (review_id,))


def add_row_stores_reviews(review_id, store_id):
    cursor.execute("""
    INSERT INTO stores_reviews (review_id, store_id)
    VALUES (%s, %s)
    """, (review_id, store_id))


def review_existence_check(review_id):
    cursor.execute("""
    SELECT review_id
    FROM reviews
    WHERE review_id = %s
    """, (review_id,))
    if not cursor.fetchone():
        raise ValueError('Review id does not exist')


def checkStoreId(source_store_id):
    cursor.execute("""
    SELECT store_id
    FROM stores
    WHERE store_id = %s
    """, (source_store_id,))
    if not cursor.fetchone():
        raise ValueError('Source store id does not exist')


def get_store_organization(source_store_id):
    cursor.execute("""
    SELECT organization_token
    FROM stores
    WHERE store_id = %s
    """, (source_store_id,))
    source_store_organization = cursor.fetchone()
    return source_store_organization


def add_row_syndicate(source_store_id, target_store_id):
    cursor.execute("""
    INSERT INTO syndicate (source_store_id, target_store_id)
    VALUES (%s, %s)
    """, (source_store_id, target_store_id))


def get_source_stores(store_id):
    cursor.execute("""
    SELECT source_store_id
    FROM syndicate
    WHERE target_store_id = %s
    """, (store_id,))
    source_stores_id = cursor.fetchall()
    return source_stores_id


def get_all_reviews(store_id):
    cursor.execute("""
    SELECT review_content
    FROM reviews
    WHERE store_id = %s
    """, store_id)
