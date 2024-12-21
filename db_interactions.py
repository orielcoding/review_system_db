from main import cursor


def checkStoreId(source_store_id):
    cursor.execute("""
    SELECT store_id
    FROM stores
    WHERE store_id = %s
    """, (source_store_id,))


def verify_token(token, store_id ): # supposed to be in a different file for credentials check
    pass