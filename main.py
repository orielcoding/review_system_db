import datetime
import random
from typing import Any

import mysql.connector
import json
import logging
from DTOs_definitions import CreateReviewRequest, UpdateReviewRequest

with open('config.json') as f:
    config = json.load(f)

connection = mysql.connector.connect(
    host=config['host'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)
cursor = connection.cursor()

# create logging file of the update - the old data and the new data
logging.basicConfig(filename=f'review_reports.log', level=logging.INFO)  # can be further improved


def create_review(request: CreateReviewRequest) -> int | None:
    """
    This function needs to make sure all fields in the request are valid.
    If not valid, print an error message and return None.
    If valid, insert the review into the database in all necessary tables.
    """
    review_content, review_rating, store_id, product_id, request_time = request

    def validate_create_request() -> bool:
        if not type(review_content) == str or not len(review_content) <= 100:
            logging.info(f'Attempted to create review with invalid content: {review_content}')
            print('Review content must be a string with less than 100 characters')
            return False
        if not type(review_rating) == int or not 1 <= review_rating <= 5:
            logging.info(f'Attempted to create review with invalid rating: {review_rating}')
            print('Review rating must be an integer between 1 and 5')
            return False
        if not type(store_id) == int:
            logging.info(f'Attempted to create review with invalid store id: {store_id}')
            print('Store id must be an integer')
            return False
        if not type(product_id) == int:
            logging.info(f'Attempted to create review with invalid product id: {product_id}')
            print('Product id must be an integer')
            return False
        if not type(request_time) == datetime.datetime:
            logging.info(f'Attempted to create review with invalid request time: {request_time}')
            print('Request time must be a datetime object')
            return False

    if not validate_create_request():
        return

    # save to reviews table
    cursor.execute("""
    INSERT INTO reviews (review_content, review_rating, store_id, product_id, request_time)
    VALUES (%s, %s, %s, %s, %s)
    """, request)

    logging.info(
        f'Created review with content: {review_content}, rating: {review_rating}, store id: {store_id}, product id: {product_id}, request time: {request_time}')

    review_id = cursor.lastrowid
    # save to stores_reviews table with generated id from mysql
    cursor.execute("""
    INSERT INTO stores_reviews (review_id, store_id)
    VALUES (%s, %s)
    """, (review_id, store_id))

    return review_id


def update_review(request: UpdateReviewRequest) -> bool:
    """
    This function needs to make sure all fields in the request are valid.
    If not valid, raise an exception.
    If valid, update the review in the database in all necessary tables.
    :return: True if the review was updated, False otherwise.
    """
    review_id, review_content, review_rating, request_time = request

    # check if review_id exists
    cursor.execute("""
    SELECT review_id
    FROM reviews
    WHERE review_id = %s
    """, (review_id,))
    if not cursor.fetchone():
        raise ValueError('Review id does not exist')

    def validate_update_request() -> bool:
        if not type(review_id) == int:
            print('Review id must be an integer')
            return False
        if not type(review_content) == str or not len(review_content) <= 100:
            print('Review content must be a string with less than 100 characters')
            return False
        if not type(review_rating) == int or not 1 <= review_rating <= 5:
            print('Review rating must be an integer between 1 and 5')
            return False
        if not type(request_time) == datetime.datetime:
            print('Request time must be a datetime object')
            return False

    if not validate_update_request():
        return False

    # print to log the old review data
    logging.info(f'Updating review with id: {review_id}')
    logging.info(f'Old review data: {cursor.fetchone()}')

    # update reviews table
    cursor.execute("""
    UPDATE reviews
    SET review_content = %s, review_rating = %s, request_time = %s
    WHERE review_id = %s
    """, (review_content, review_rating, request_time, review_id))

    # log the new data
    logging.info(f'New data: {cursor.fetchone()}')

    return True


def delete_review(review_id: int) -> bool:
    """
    This function needs to delete the review from the database in all necessary tables.
    return True if the review was deleted, False otherwise.
    """

    # check if review_id exists
    cursor.execute("""
    SELECT review_id
    FROM reviews
    WHERE review_id = %s
    """, (review_id,))
    if not cursor.fetchone():
        logging.info(f'Attempted to delete review with non existing id: {review_id} and failed.')
        print('Review id does not exist')
        return False

    # delete from reviews table
    cursor.execute("""
    DELETE FROM reviews
    WHERE review_id = %s
    """, (review_id,))

    logging.info(f'Deleted review with id: {review_id} from reviews table.')

    # delete from stores_reviews table
    cursor.execute("""
    DELETE FROM stores_reviews
    WHERE review_id = %s
    """, (review_id,))

    logging.info(f'Deleted review with id: {review_id} from stores_reviews table.')

    return True


def get_reviews(store_id: int) -> list:
    """
    return all reviews for a given store including syndicated reviews according to syndication rules.
    """
    pass


def syndicate_stores(source_store_id: int, target_store_id: int) -> bool:
    """
    Syndicate reviews from source_store_id to target_store_id according to syndication rules.
    The target store is the client's store. The source store is the store that the client
    wants to syndicate reviews from.
    """
    pass


def main():
    pass


if __name__ == '__main__':
    main()
