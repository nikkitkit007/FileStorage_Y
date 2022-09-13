from datetime import datetime, timedelta
import os
import config
from sqlalchemy.schema import CreateSchema
from .base import Base, engine, session

from .schema_db import SystemItem, SystemItemHistory


def create_functions():
    with session(bind=engine) as local_session:
        local_session.execute(f"""
        CREATE OR REPLACE FUNCTION {config.SCHEMA_NAME}.upd_size(id_add_item varchar, change_size integer) RETURNS INTEGER AS $$
        BEGIN
            SET session_replication_role = replica;
            WITH RECURSIVE r AS (
                SELECT {config.SCHEMA_NAME}."SystemItem"."id", {config.SCHEMA_NAME}."SystemItem"."parentId", "ItemStorage"."SystemItem"."size"
                FROM {config.SCHEMA_NAME}."SystemItem"
                WHERE "id" = id_add_item
        
                UNION
        
                SELECT {config.SCHEMA_NAME}."SystemItem"."id", {config.SCHEMA_NAME}."SystemItem"."parentId", {config.SCHEMA_NAME}."SystemItem"."size"
                FROM {config.SCHEMA_NAME}."SystemItem"
                  JOIN r
                      ON {config.SCHEMA_NAME}."SystemItem"."id" = r."parentId"
            )
            UPDATE {config.SCHEMA_NAME}."SystemItem"
            SET "size" = "size" + change_size
            WHERE {config.SCHEMA_NAME}."SystemItem"."id"
            in (SELECT "parentId" FROM r);
            SET session_replication_role = DEFAULT;
        RETURN NULL;
        END
        $$ LANGUAGE plpgsql;
        """)
        local_session.execute("""
        CREATE OR REPLACE FUNCTION "ItemStorage".upd_date(id_add_item varchar, date_upd timestamp, delete_node bool) RETURNS INTEGER AS $$
        BEGIN
            SET session_replication_role = replica;
            CREATE TEMP TABLE recur_table ON COMMIT DROP AS WITH RECURSIVE r AS (
                SELECT "ItemStorage"."SystemItem"."id", "ItemStorage"."SystemItem"."parentId", "ItemStorage"."SystemItem"."size"
                FROM "ItemStorage"."SystemItem"
                WHERE "id" = id_add_item
        
                UNION
        
                SELECT "ItemStorage"."SystemItem"."id", "ItemStorage"."SystemItem"."parentId", "ItemStorage"."SystemItem"."size"
                FROM "ItemStorage"."SystemItem"
                  JOIN r
                      ON "ItemStorage"."SystemItem"."id" = r."parentId"
            ) SELECT * FROM r;
            IF NOT delete_node THEN
            INSERT INTO "ItemStorage"."SystemItemHistory" ("id_original", "url", "date", "parentId", "type", "size")
            SELECT "id", "url", "date", "parentId", "type", "size" FROM "ItemStorage"."SystemItem"
            WHERE "ItemStorage"."SystemItem"."id" in (SELECT "id" FROM recur_table);
            ELSE
            DELETE FROM "ItemStorage"."SystemItemHistory" WHERE "id_original" in (SELECT "id" FROM recur_table);
            END IF;
            UPDATE "ItemStorage"."SystemItem"
            SET "date" = date_upd
            WHERE "ItemStorage"."SystemItem"."id"
            in (SELECT "parentId" FROM recur_table);
            SET session_replication_role = DEFAULT;
        RETURN NULL;
        END
        $$ LANGUAGE plpgsql;
        """)
        local_session.execute("""
        CREATE OR REPLACE FUNCTION "ItemStorage".insert_dependencies() RETURNS TRIGGER AS $$
        BEGIN
        PERFORM "ItemStorage".upd_size(NEW."id", NEW."size");
        PERFORM "ItemStorage".upd_date(NEW."id", NEW."date", False);
        RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """)
        local_session.execute("""
        CREATE OR REPLACE FUNCTION "ItemStorage".update_dependencies() RETURNS TRIGGER AS $$
        BEGIN
        PERFORM "ItemStorage".upd_size(OLD."id", -OLD."size");
        PERFORM "ItemStorage".upd_size(NEW."id", NEW."size");
        PERFORM "ItemStorage".upd_date(NEW."id", NEW."date", False);
        RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """)
        local_session.execute("""
        CREATE OR REPLACE FUNCTION "ItemStorage".delete_dependencies() RETURNS TRIGGER AS $$
        BEGIN
        PERFORM "ItemStorage".upd_size(OLD."id", -OLD."size");
        PERFORM "ItemStorage".upd_date(OLD."id", OLD."date", True);
        RETURN OLD;
        END
        $$ LANGUAGE plpgsql;
        """)


def create_trigger():
    with session(bind=engine) as local_session:
        local_session.execute("""
        CREATE OR REPLACE TRIGGER insert_dependencies_trigger
            AFTER INSERT ON "ItemStorage"."SystemItem"
            FOR EACH ROW
            EXECUTE FUNCTION "ItemStorage".insert_dependencies();
        """)
        local_session.execute("""
        CREATE OR REPLACE TRIGGER update_dependencies_trigger
            AFTER UPDATE ON "ItemStorage"."SystemItem"
            FOR EACH ROW
            EXECUTE FUNCTION "ItemStorage".update_dependencies();
        """)
        local_session.execute("""
        CREATE OR REPLACE TRIGGER delete_dependencies_trigger
            AFTER DELETE ON "ItemStorage"."SystemItem"
            FOR EACH ROW
            EXECUTE FUNCTION "ItemStorage".delete_dependencies();
        """)


def create_all_tables():
    Base.metadata.create_all(engine)


def create_schema():
    engine.execute(CreateSchema(config.SCHEMA_NAME))


def create_db():
    if not engine.dialect.has_schema(engine, config.SCHEMA_NAME):
        create_schema()
    create_all_tables()
    create_functions()
    create_trigger()


def main():
    sys_items1 = {
        "items":
            [
                {
                    "id": "4",
                    "url": "/file/url1",
                    "parentId": "3",
                    "size": 1024,
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
                    "id": "3",
                    "parentId": "1",
                    "size": 128,
                    "children": None
                }
            ],
        "updateDate": "2022-09-11T21:12:01.000Z"

    }
    SystemItem.add(sys_items1)
    children = SystemItem.get_children({"id": "1"})
    print(children)


if __name__ == '__main__':
    create_db()
    main()
    # isoformat
