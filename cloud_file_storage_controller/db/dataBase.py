
import config
from sqlalchemy.schema import CreateSchema
from .base import Base, engine, session


class DataBaseSchema:

    @staticmethod
    def create_functions():
        with session(bind=engine) as local_session:
            local_session.execute("""
            CREATE OR REPLACE FUNCTION "ItemStorage".upd_size(id_add_item varchar, change_size integer) RETURNS INTEGER AS $$
            BEGIN
                SET session_replication_role = replica;
                WITH RECURSIVE r AS (
                    SELECT "ItemStorage"."SystemItem"."id", "ItemStorage"."SystemItem"."parentId", "ItemStorage"."SystemItem"."size"
                    FROM "ItemStorage"."SystemItem"
                    WHERE "id" = id_add_item

                    UNION

                    SELECT "ItemStorage"."SystemItem"."id", "ItemStorage"."SystemItem"."parentId", "ItemStorage"."SystemItem"."size"
                    FROM "ItemStorage"."SystemItem"
                      JOIN r
                          ON "ItemStorage"."SystemItem"."id" = r."parentId"
                )
                UPDATE "ItemStorage"."SystemItem"
                SET "size" = "size" + change_size
                WHERE "ItemStorage"."SystemItem"."id"
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

    @staticmethod
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

    @staticmethod
    def create_all_tables():
        Base.metadata.create_all(engine)

    @staticmethod
    def create_schema():
        engine.execute(CreateSchema(config.SCHEMA_NAME))

    @staticmethod
    def create_db():
        if not engine.dialect.has_schema(engine, config.SCHEMA_NAME):
            DataBaseSchema.create_schema()
            DataBaseSchema.create_all_tables()
            DataBaseSchema.create_functions()
            DataBaseSchema.create_trigger()


if __name__ == '__main__':
    DataBaseSchema.create_db()


