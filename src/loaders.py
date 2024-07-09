""" 
Usage:

In a Unix terminal window, cd to parent directory of the "src" directory.

# activate virtual env
pipenv shell
# run as a module
python -m src.loaders
"""

from src.database import engine
from src.models import Base, Department, Aisle, Product, Section
from src.data import load_data


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
        "products",
        "sections",
    ]
    mapper_names = [
        #
        ("departments", Department),
        ("aisles", Aisle),
        ("products", Product),
        ("sections", Section),
    ]
    # for table_name, obj in mapper_names:
    #     # need to bet table from the table name
    #     mapper(obj, table)
    tables = [Base.metadata.tables[name] for name in table_names]
    Base.metadata.create_all(engine, tables, checkfirst=True)


if __name__ == "__main__":
    # create_database()
    print(load_data.get_departments_with_rank())
    # load_data.insert_all_departments()
    # load_data.insert_all_aisles_with_rank()
    # load_data.insert_item_by_index(0)
    # load_data.insert_all_products()
    # load_data.update_all_product_details()
    # load_data.insert_section_by_index(0)
    # load_data.insert_all_sections()
