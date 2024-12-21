from flask import Flask, jsonify, request
from main import *
from DTOs_definitions import CreateReviewRequest, UpdateReviewRequest
from pydantic import ValidationError
from db_interactions import verify_token

app = Flask(__name__)

@app.route('/reviews', methods=['POST'])
def create_review_route():

    # examine clients' token to verify his permission to access the store reviews
    token = request.headers.get("Authorization")  # simulate the client's token

    if not verify_token(token, **request.json['store_id']):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    try:
        # Parse and validate the request JSON using the DTO
        CreateReviewRequest(**request.json)
    except ValidationError as e:
        # Fail in validation by the DTO
        return jsonify({"errors": e.errors()}), 400

    # Attempt to create the review
    review_id = create_review(**request.json)

    # Case: fail in rules of the business
    if review_id is None:
        return jsonify({"error": "Failed to create review"}), 400

    # Case: success processing of the request
    return jsonify({'review_id': review_id}), 201


@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review_route(review_id: int):

    # examine clients' token to verify his permission to access the store reviews
    token = request.headers.get("Authorization")  # simulate the client's token

    if not verify_token(token, **request.json['store_id']):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    try:
        # Parse and validate the request JSON using the DTO
        data = UpdateReviewRequest(**request.json)
    except ValidationError as e:
        # Fail in validation by the DTO
        return jsonify({"errors": e.errors()}), 400

    # Attempt to update the review
    success = update_review(data)

    # Case: fail in rules of the business
    if not success:
        return jsonify({"error": "Failed to update review"}), 400

    # Case: success processing of the request
    return jsonify({'message': 'Review updated successfully'}), 200


@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review_route(review_id: int):

    # examine clients' token to verify his permission to access the store reviews
    token = request.headers.get("Authorization")  # simulate the client's token

    if not verify_token(token, **request.json['store_id']):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    # Attempt to delete the review
    success = delete_review(review_id)

    # Case: fail in rules of the business
    if not success:
        return jsonify({"error": "Failed to delete review"}), 400

    # Case: success processing of the request
    return jsonify({'message': 'Review deleted successfully'}), 204


@app.route('/reviews', methods=['GET'])
def get_reviews_route(store_id: int):

    # examine clients' token to verify his permission to access the store reviews
    token = request.headers.get("Authorization")  # simulate the client's token

    if not verify_token(token, store_id):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    # Attempt to get the reviews
    reviews = get_reviews(store_id)

    # Case: fail in rules of the business
    if not reviews:
        return jsonify({f"error": f"store id: {store_id} don't exist."}), 404  # Could be a security issue need addressing

    # Case: success processing of the request
    return jsonify(reviews), 200


@app.route('/syndicate', methods=['POST'])
def syndicate_stores_route():

    # examine clients' token to verify his permission to access the store reviews
    token = request.headers.get("Authorization")  # simulate the client's token

    if not verify_token(token, **request.json['store_id']):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    source_store_id = request.json['source_store_id']
    target_store_id = request.json['target_store_id']

    # Attempt to syndicate the reviews
    success = syndicate_stores(source_store_id, target_store_id)

    # Case: fail in rules of the business
    if not success:
        return jsonify({"error": "Failed to syndicate reviews"}), 404  # don't separate the type of 404 currently.

    # Case: success processing of the request
    return jsonify({'message': 'Reviews syndicated successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
