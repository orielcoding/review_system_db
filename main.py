import datetime
import random
import mysql.connector
import json
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


def create_review(request: CreateReviewRequest) -> int:
    """
    This function needs to make sure all fields in the request are valid.
    If not valid, raise an exception.
    If valid, insert the review into the database in all necessary tables.
    """
    pass


def update_review(request: UpdateReviewRequest) -> bool:
    """
    This function needs to make sure all fields in the request are valid.
    If not valid, raise an exception.
    If valid, update the review in the database in all necessary tables.
    :return: True if the review was updated, False otherwise.
    """
    pass


def delete_review(review_id: int) -> bool:
    """
    This function needs to delete the review from the database in all necessary tables.
    return True if the review was deleted, False otherwise.
    """
    pass


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
