import json
import os
from sqlalchemy import create_engine, MetaData, Table, insert
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from models import Items

SQLALCHEMY_DATABASE_URL = "sqlite:///./costco.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
connection = engine.connect()
# session = sessionmaker()
# session.configure(bind=engine)
# my_session = session()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


root_path = os.path.dirname(__file__)

db_cache = {}
data_cache = {}


def get_items():
    if "items" in data_cache:
        return data_cache["items"]
    file_name = os.path.join(root_path, "items.json")
    print(file_name)
    with open(file_name) as items_file:
        file_contents = items_file.read()
        # print(file_contents)
        items = json.loads(file_contents)
    data_cache["items"] = items
    return data_cache["items"]


def insert_item(table: Table, item: dict):
    KEYS = [
        #
        "name",
        "product_id",
        "href",
        "src",
        "alt",
        "price",
    ]
    values = {key: item[key] for key in KEYS}
    USE_STATEMENT = False
    if USE_STATEMENT:
        stmt = insert(table).values(**values)
        result = connection.execute(stmt)
        connection.commit()
        return result
    else:
        new_item = Items(**values)
        # db = get_db()
        # db.add(new_item)
        # db.commit()
        with next(get_db()) as db:
            db.add(new_item)
            db.commit()


def get_table(table_name):
    if table_name in db_cache:
        return db_cache[table_name]
    metadata_obj = MetaData()
    table = Table(table_name, metadata_obj, autoload_with=engine)
    for c in table.c:
        print(c)
    db_cache[table_name] = table
    return table


def insert_item_by_index(index: int):
    items = get_items()
    print(f"Number of items = {len(items)}")
    items_table = get_table("items")
    product_ids = list(items.keys())
    insert_item(table=items_table, item=items[product_ids[index]])


if __name__ == "__main__":
    print("main")
    items = get_items()
    print(f"Number of items = {len(items)}")
    items_table = get_table("items")
    product_ids = list(items.keys())
    index = 2
    # print(items[product_ids[index]])
    insert_item(table=items_table, item=items[product_ids[index]])
