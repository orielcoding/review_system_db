from main import cursor


def checkStoreId(source_store_id):
    cursor.execute("""
    SELECT store_id
    FROM stores
    WHERE store_id = %s
    """, (source_store_id,))
