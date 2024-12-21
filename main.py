import datetime
import mysql.connector
import json
import logging
from DTOs_definitions import CreateReviewRequest, UpdateReviewRequest
from db_interactions import checkStoreId

with open('config.json') as f:
    config = json.load(f)

connection = mysql.connector.connect(  # TODO: separate concerns - all db actions in db_interactions.py
    host=config['host'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)
cursor = connection.cursor()

# create logging file for create, update, delete and get functions altogether.
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


def syndicate_stores(source_store_id: int, target_store_id: int) -> bool:  # TODO: correct the function - understand the requirements
    """
    Syndicate reviews from source_store_id to target_store_id according to syndication rules.
    The target store is the client's store. The source store is the store that the client
    wants to syndicate reviews from.
    """

    # check if source_store_id exists
    checkStoreId(source_store_id)
    if not cursor.fetchone():
        logging.info(f'Attempted to syndicate reviews from non existing source store id: {source_store_id} and failed.')
        print('Source store id does not exist')
        return False

    # check if target_store_id exists
    checkStoreId(target_store_id)
    if not cursor.fetchone():
        logging.info(f'Attempted to syndicate reviews to non existing target store id: {target_store_id} and failed.')
        print('Target store id does not exist')
        return False

    # check source and target store organization
    cursor.execute("""
    SELECT organization_token
    FROM stores
    WHERE store_id = %s
    """, (source_store_id,))
    source_store_organization = cursor.fetchone()

    cursor.execute("""
    SELECT organization_token
    FROM stores
    WHERE store_id = %s
    """, (target_store_id,))
    target_store_organization = cursor.fetchone()

    # check if source and target store belong to the same organization
    if source_store_organization != target_store_organization:
        logging.info(f'Attempted to syndicate reviews from different organizations and failed.')
        print('Stores are not in the same organization')
        return False

    # add row in syndicate table
    cursor.execute("""
    INSERT INTO syndicate (source_store_id, target_store_id)
    VALUES (%s, %s)
    """, (source_store_id, target_store_id))

    logging.info(f'Successfully syndicated reviews from source store id: {source_store_id} to target store id: {target_store_id}.')
    return True


def get_reviews(store_id: int) -> list:
    """
    Return target store reviews and all the reviews whose their store syndicated to the target store.
    Note: currently, it returns only the review content, but it can be extended to return rating and request time.
    :param store_id - the target store from which a client want to extract reviews.
    """

    # examine clients' token to verify the store he belongs to.
    if not credentials_check(target_store_id, token):  # TODO: separate concerns
        print('stores are not in the same organization')
        return []

    # check all source stores that syndicate to the target store
    cursor.execute("""
    SELECT source_store_id
    FROM syndicate
    WHERE target_store_id = %s
    """, (store_id,))
    source_stores_id = cursor.fetchall()

    # get reviews contents alone from the target store - not including any database access
    reviews = []
    # get reviuews from target store
    cursor.execute("""
    SELECT review_content
    FROM reviews
    WHERE store_id = %s
    """, store_id)
    rows = cursor.fetchall()
    # the rows are tuples. add the data to reviews as json string
    reviews.extend([row[0] for row in rows])

    logging.info(f'Getting reviews from target store id: {store_id}')  # here I can add more advanced logging

    # get reviews from source stores
    for source_store_id in source_stores_id:
        syndicate_stores(source_store_id, store_id)
        cursor.execute("""
        SELECT review_content
        FROM reviews
        WHERE store_id = %s
        """, source_store_id)

        logging.info(f'Getting reviews from source store id: {source_store_id}')  # here I can add more advanced logging

        rows = cursor.fetchall()
        reviews.extend([row[0] for row in rows])

    return reviews


def main():
    pass


if __name__ == '__main__':
    main()
