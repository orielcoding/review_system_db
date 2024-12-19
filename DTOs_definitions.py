import datetime


class CreateReviewRequest:
    # Define attributes with name mangling to make them private (a bit different from Java)
    def __init__(self, review, rating, store_id, product_id, request_time):
        self.__review_content: str = review
        self.__review_rating: int = rating
        self.__store_id: int = store_id
        self.__product_id: int = product_id
        self.__request_time: datetime.datetime = request_time


class UpdateReviewRequest:
    def __init__(self, review_id, review, rating, request_time):
        self.__review_id: int = review_id
        self.__review_content: str = review
        self.__review_rating: int = rating
        self.__request_time: datetime.datetime = request_time