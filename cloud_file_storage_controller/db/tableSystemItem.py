import config
import sqlalchemy as sa
from .base import Base, session, engine


TYPES = ["FILE", "FOLDER"]


class SystemItem(Base):
    __tablename__ = config.TBL_SystemItem

    id = sa.Column('id', sa.String, primary_key=True, nullable=False)
    url = sa.Column('url', sa.String(255), nullable=True)
    date = sa.Column('date', sa.TIMESTAMP, nullable=False)
    parentId = sa.Column('parentId', sa.String(255), nullable=True)
    type = sa.Column('type', sa.String(64), nullable=False)
    size = sa.Column('size', sa.Integer, nullable=True)

    def __init__(self, system_item_data):
        try:
            self.id = system_item_data['id']
            self.url = system_item_data.get('url', None)
            self.date = system_item_data['date']
            self.parentId = system_item_data['parentId']
            self.size = system_item_data.get('size', 0)
            item_type = system_item_data['type']
            assert item_type in TYPES
            self.type = item_type
            # if self.type == "FOLDER":
            #     assert self.url is None and self.size is None
            # else:
            #     assert self.url is not None and self.size is not None
        except Exception:
            raise ValueError

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
                    item.url = sys_item.get("url", None)
                    item.parentId = sys_item["parentId"]
                    item.size = sys_item.get("size", None)
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
        return item_to_delete

    @staticmethod
    def get(item_id: str):
        with session(bind=engine) as local_session:
            item = local_session.query(SystemItem).filter(SystemItem.id == item_id).first()
            if item:
                return SystemItem.get_dict(item)
            else:
                return None

    @staticmethod
    def get_children(folder: dict):
        with session(bind=engine) as local_session:
            _children = local_session.query(SystemItem).filter(SystemItem.parentId == folder["id"]).all()
            children = []
            for child in _children:
                child = SystemItem.get_dict(child)
                child['children'] = SystemItem.get_children(child)
                children.append(child)
        return children if children else None

    @staticmethod
    def get_items_in_interval(date_start: str, date_end: str):
        with session(bind=engine) as local_session:
            items = {"items": []}
            items_recent = local_session.query(SystemItem). \
                filter((SystemItem.date >= date_start) &
                       (SystemItem.date < date_end) &
                       (SystemItem.type == "FILE")).all()
            for item in items_recent:
                items["items"].append(SystemItem.get_dict(item))

            local_session.commit()
        return items
