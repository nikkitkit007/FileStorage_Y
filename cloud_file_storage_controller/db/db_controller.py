from datetime import datetime, timedelta
import os
import config
from sqlalchemy.schema import CreateSchema
from base import Base, engine

from schema_db import SystemItem


def create_all_tables():
    Base.metadata.create_all(engine)


def create_schema():
    engine.execute(CreateSchema(config.SCHEMA_NAME))


def create_db():
    if not engine.dialect.has_schema(engine, config.SCHEMA_NAME):
        create_schema()
    create_all_tables()
    pass


def main():
    sys_items = {
        "items":
            [
                {
                    "id": "9",
                    "url": "/file/url1",
                    "parentId": "7",
                    "size": 128,
                    "type": "FILE"
                }
            ],
        "updateDate": "2022-09-11T21:12:01.000Z"
    }
    sys_items2 = {
        "items":
            [
                {
                    "type": "FOLDER",
                    "url": "/file/url56",
                    "id": "7",
                    "parentId": "5",
                    "size": 128,
                    "children": None
                }
            ],
        "updateDate": "2022-09-11T21:12:01.000Z"

    }
    SystemItem.add(sys_items)

    # SystemItem.delete({"id": "элемент_1_4"})
    # print(SystemItem.get_children({"id": "элемент_1_4"}))

    # data_find = (datetime.now() - timedelta(5)).isoformat()
    # print(SystemItem.get_recent(data_find))

    # data_find_start = (datetime.now() - timedelta(5)).isoformat()
    # data_find_end = (datetime.now()).isoformat()
    # print(SystemItem.get_items_in_interval(data_find_start, data_find_end))


if __name__ == '__main__':
    create_db()
    main()
    # isoformat
