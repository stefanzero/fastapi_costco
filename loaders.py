from database import engine
from models import Base
from data import load_data


def create_database():
    """
    Need to create tables with foreign keys after their related table
    has been created:
    - departments has no foreign keys
    - aisles references departments
    - item references aisles
    """

    table_names = [
        #
        "departments",
        "aisles",
        "items",
        "sections",
    ]
    tables = [Base.metadata.tables[name] for name in table_names]
    Base.metadata.create_all(engine, tables, checkfirst=True)


if __name__ == "__main__":
    create_database()
    # load_data.insert_all_departments()
    # load_data.insert_all_aisles()
    # load_data.insert_item_by_index(0)
    # load_data.insert_all_items()
    # load_data.insert_section_by_index(0)
    load_data.insert_all_sections()
