import config
import sqlalchemy as sa
from .base import Base, session, engine
from typing import Optional

from logger_config import info_logger, error_logger


class SystemItemHistory(Base):
    __tablename__ = config.TBL_SystemItemHistory

    id = sa.Column('id', sa.Integer, primary_key=True)
    id_original = sa.Column('id_original', sa.String, nullable=True)        # TODO: FOREIGN KEY
    url = sa.Column('url', sa.String(255), nullable=True)
    date = sa.Column('date', sa.TIMESTAMP, nullable=False)
    parentId = sa.Column('parentId', sa.String(255), nullable=True)
    type = sa.Column('type', sa.String(64), nullable=False)
    size = sa.Column('size', sa.Integer, nullable=True)

    def __init__(self, system_item_data):
        try:

            self.id_original = system_item_data['id_original']
            self.url = system_item_data.get('url', None)
            self.date = system_item_data['date']
            self.parentId = system_item_data['parentId']
            self.size = system_item_data.get('size', 0)
            self.type = system_item_data['type']

        except Exception:
            raise ValueError

    def get_dict(self):
        atts_dict = {"id": self.id_original,
                     "url": self.url,
                     "date": self.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "parentId": self.parentId,
                     "type": self.type,
                     "size": self.size}

        return atts_dict

    @staticmethod
    def get_items_in_interval(item_id: str, date_start: str, date_end: str):
        with session(bind=engine) as local_session:
            items = {"items": []}
            items_recent = local_session.query(SystemItemHistory). \
                filter((SystemItemHistory.date >= date_start) &
                       (SystemItemHistory.date < date_end) &
                       (SystemItemHistory.id_original == item_id)).all()
            for item in items_recent:
                items["items"].append(SystemItemHistory.get_dict(item))

            local_session.commit()
        return items


if __name__ == "__main__":
    pass
