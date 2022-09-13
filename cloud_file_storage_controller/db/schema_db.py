import config
from copy import deepcopy
import sqlalchemy as sa
from datetime import datetime
from base import Base, session, engine
from typing import Optional

from logger_config import info_logger, error_logger

TYPES = ["FILE", "FOLDER"]


class SystemItem(Base):
    __tablename__ = config.TBL

    id = sa.Column('id', sa.String, primary_key=True, nullable=False)
    url = sa.Column('url', sa.String(255), nullable=True)
    date = sa.Column('date', sa.TIMESTAMP, nullable=False)
    parentId = sa.Column('parentId', sa.String(255), nullable=True)
    type = sa.Column('type', sa.String(64), nullable=False)
    size = sa.Column('size', sa.Integer, nullable=False)

    def __init__(self, system_item_data):
        self.id = system_item_data['id']
        self.url = system_item_data['url']
        self.date = system_item_data['date']
        self.parentId = system_item_data['parentId']
        self.size = system_item_data['size']

        item_type = system_item_data['type']
        if item_type in TYPES:
            self.type = item_type

    def get_dict(self):
        atts_dict = {"id": self.id,
                     "url": self.url,
                     "date": self.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "parentId": self.parentId,
                     "type": self.type,
                     "size": self.size}
        return atts_dict

    @staticmethod
    def add(sys_items_to_add: dict):
        with session(bind=engine) as local_session:
            for sys_item in sys_items_to_add["items"]:
                sys_item_id = sys_item["id"]
                item = local_session.query(SystemItem).filter(SystemItem.id == sys_item_id).first()
                if item:
                    item.url = sys_item["url"]
                    item.parentId = sys_item["parentId"]
                    item.size = sys_item["size"]
                    item.type = sys_item["type"]
                    item.date = sys_items_to_add["updateDate"]
                else:
                    sys_item["date"] = sys_items_to_add["updateDate"]
                    local_session.add(SystemItem(sys_item))

                local_session.commit()

    @staticmethod
    def delete(id_item_to_delete: dict):
        with session(bind=engine) as local_session:
            item_to_delete = local_session.query(SystemItem).filter(SystemItem.id == id_item_to_delete["id"]).first()
            if item_to_delete:
                local_session.delete(item_to_delete)
                local_session.commit()
            local_session.commit()

    @staticmethod
    def get_children(folder: dict):
        with session(bind=engine) as local_session:
            folder_data = local_session.query(SystemItem).filter(SystemItem.id == folder["id"]).first()
            folder_dict = SystemItem.get_dict(folder_data)
            children_ids = folder_data.children
            for i, children_id in enumerate(children_ids):
                item_children = local_session.query(SystemItem).filter(SystemItem.id == children_id).first()
                folder_dict["children"][i] = item_children
            local_session.commit()
        return folder_dict

    @staticmethod
    def get_recent(date: str):
        with session(bind=engine) as local_session:
            items = {"items": []}
            items_recent = local_session.query(SystemItem).filter(SystemItem.date >= date).all()
            for item in items_recent:
                items["items"].append(SystemItem.get_dict(item))

            local_session.commit()
        return items

    @staticmethod
    def get_items_in_interval(date_start: str, date_end: str):
        with session(bind=engine) as local_session:
            items = {"items": []}
            items_recent = local_session.query(SystemItem). \
                filter((SystemItem.date >= date_start) & (SystemItem.date < date_end)).all()
            for item in items_recent:
                items["items"].append(SystemItem.get_dict(item))

            local_session.commit()
        return items


if __name__ == "__main__":
    pass
