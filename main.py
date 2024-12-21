import logging
from DTOs_definitions import *
from db_interactions import *


# create a single logging file. It can be further improved to separate logs for each function / db table / client.
logging.basicConfig(filename=f'review_reports.log', level=logging.INFO)


def create_review(request: CreateReviewRequest) -> int | None:
    """
    This function needs to make sure all fields in the request are valid.
    If not valid, print an error message and return None.
    If valid, insert the review into the database in all necessary tables.
    """
    review_content, review_rating, store_id, product_id, request_time = request

    def validate_create_request() -> bool:  # TODO: separate concerns to app after merging, the rules should remain here
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
    add_row_reviews(request)
    logging.info(
        f'Created review with content: {review_content}, rating: {review_rating}, store id: {store_id}, product id: {product_id}, request time: {request_time}')

    review_id = cursor.lastrowid

    # save to stores_reviews table with generated id from mysql
    add_row_stores_reviews(review_id, store_id)
    logging.info(f'Created review with id: {review_id} in stores_reviews table.')

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
    try:
        review_existence_check(review_id)
    except ValueError as e:
        print(e)
        return False

    def validate_update_request() -> bool:  # TODO: separate concerns to app after merging, the rules should remain here
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
    update_reviews_table(request_time, review_content, review_id, review_rating)

    # log the new data
    logging.info(f'New data: {cursor.fetchone()}')

    return True


def delete_review(review_id: int) -> bool:
    """
    This function needs to delete the review from the database in all necessary tables.
    return True if the review was deleted, False otherwise.
    """

    # check if review_id exists
    try:
        review_existence_check(review_id)
    except ValueError as e:
        print(e)
        return False

    # delete from reviews table
    delete_from_reviews(review_id)
    logging.info(f'Deleted review with id: {review_id} from reviews table.')

    # delete from stores_reviews table
    delete_from_stores_reviews(review_id)
    logging.info(f'Deleted review with id: {review_id} from stores_reviews table.')

    return True


def syndicate_stores(source_store_id: int, target_store_id: int) -> bool:
    """
    Syndicate reviews from source_store_id to target_store_id according to syndication rules.
    The target store is the client's store. The source store is the store that the client
    wants to syndicate reviews from.
    """

    # check if source_store_id exists
    try:
        checkStoreId(source_store_id)
    except ValueError as e:
        print('Source store id does not exist')
        logging.info(f'Attempted to syndicate reviews from non existing source store id: {source_store_id} and failed.')
        return False

    # check if target_store_id exists
    try:
        checkStoreId(target_store_id)
    except ValueError as e:
        print('Source store id does not exist')
        logging.info(f'Attempted to syndicate reviews from non existing source store id: {source_store_id} and failed.')
        return False

    # check source and target store organization
    source_store_organization = get_store_organization(source_store_id)
    target_store_organization = get_store_organization(target_store_id)

    # check if source and target store belong to the same organization
    if source_store_organization != target_store_organization:
        logging.info(f'Attempted to syndicate reviews from different organizations and failed.')
        print('Stores are not in the same organization')
        return False

    # add row in syndicate table
    add_row_syndicate(source_store_id, target_store_id)

    logging.info(f'Successfully syndicated reviews from source store id: {source_store_id} to target store id: {target_store_id}.')
    return True


def get_reviews(store_id: int) -> list:
    """
    Return target store reviews and all the reviews whose their store syndicated to the target store.
    Note: currently, it returns only the review content, but it can be extended to return rating and request time.
    :param store_id - the target store from which a client want to extract reviews.
    """

    # check all source stores that syndicate to the target store
    source_stores_id = get_source_stores(store_id)

    # get reviews contents alone from the target store - not including any database access
    reviews = []
    # get reviews from target store
    get_all_reviews(store_id)
    rows = cursor.fetchall()
    # the rows are tuples. add the data to reviews as json string
    reviews.extend([row[0] for row in rows])

    logging.info(f'Getting reviews from target store id: {store_id}')  # here I can add more advanced logging

    # get reviews from source stores
    for source_store_id in source_stores_id:
        syndicate_stores(source_store_id, store_id)
        get_all_reviews(source_store_id)

        logging.info(f'Getting reviews from source store id: {source_store_id}')  # here I can add more advanced logging

        rows = cursor.fetchall()
        reviews.extend([row[0] for row in rows])

    return reviews
