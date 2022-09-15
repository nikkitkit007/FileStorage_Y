
import config
from sqlalchemy.schema import CreateSchema
from .base import Base, engine, session


class DataBaseSchema:

    @staticmethod
    def create_functions():
        schema_table_name_main = f"\"{config.SCHEMA_NAME}\".\"{config.TBL_SystemItem}\""
        schema_table_name_history = f"\"{config.SCHEMA_NAME}\".\"{config.TBL_SystemItemHistory}\""

        with session(bind=engine) as local_session:
            # FUNCTION update size
            local_session.execute(f"""
                CREATE OR REPLACE FUNCTION \"{config.SCHEMA_NAME}\".upd_size(id_add_item varchar, change_size integer) 
                RETURNS INTEGER AS $$
                BEGIN
                    SET session_replication_role = replica;
                    WITH RECURSIVE r AS (
                        SELECT {schema_table_name_main}."id", {schema_table_name_main}."parentId", {schema_table_name_main}."size"
                        FROM {schema_table_name_main}
                        WHERE "id" = id_add_item

                        UNION

                        SELECT {schema_table_name_main}."id", {schema_table_name_main}."parentId", {schema_table_name_main}."size"
                        FROM {schema_table_name_main}
                          JOIN r
                              ON {schema_table_name_main}."id" = r."parentId"
                    )
                    UPDATE {schema_table_name_main}
                    SET "size" = "size" + change_size
                    WHERE {schema_table_name_main}."id"
                    in (SELECT "parentId" FROM r);
                    SET session_replication_role = DEFAULT;
                RETURN NULL;
                END
                $$ LANGUAGE plpgsql;
                """)
            # FUNCTION update date
            local_session.execute(f"""
                CREATE OR REPLACE FUNCTION \"{config.SCHEMA_NAME}\".upd_date(id_add_item varchar, date_upd timestamp, delete_node bool) RETURNS INTEGER AS $$
                BEGIN
                    SET session_replication_role = replica;
                    CREATE TEMP TABLE recur_table ON COMMIT DROP AS WITH RECURSIVE r AS (
                        SELECT {schema_table_name_main}."id", {schema_table_name_main}."parentId", {schema_table_name_main}."size"
                        FROM {schema_table_name_main}
                        WHERE "id" = id_add_item

                        UNION

                        SELECT {schema_table_name_main}."id", {schema_table_name_main}."parentId", {schema_table_name_main}."size"
                        FROM {schema_table_name_main}
                          JOIN r
                              ON {schema_table_name_main}."id" = r."parentId"
                    ) SELECT * FROM r;
                    IF NOT delete_node THEN
                    INSERT INTO {schema_table_name_history} ("id_original", "url", "date", "parentId", "type", "size")
                    SELECT "id", "url", "date", "parentId", "type", "size" FROM {schema_table_name_main}
                    WHERE {schema_table_name_main}."id" in (SELECT "id" FROM recur_table);
                    ELSE
                    DELETE FROM {schema_table_name_history} WHERE "id_original" in (SELECT "id" FROM recur_table);
                    END IF;
                    UPDATE {schema_table_name_main}
                    SET "date" = date_upd
                    WHERE {schema_table_name_main}."id"
                    in (SELECT "parentId" FROM recur_table);
                    SET session_replication_role = DEFAULT;
                RETURN NULL;
                END
                $$ LANGUAGE plpgsql;
                """)
            # FUNCTION insert dependencies
            local_session.execute(f"""
                CREATE OR REPLACE FUNCTION \"{config.SCHEMA_NAME}\".insert_dependencies() RETURNS TRIGGER AS $$
                BEGIN
                PERFORM \"{config.SCHEMA_NAME}\".upd_size(NEW."id", NEW."size");
                PERFORM \"{config.SCHEMA_NAME}\".upd_date(NEW."id", NEW."date", False);
                RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
                """)
            # FUNCTION update dependencies
            local_session.execute(f"""
                CREATE OR REPLACE FUNCTION \"{config.SCHEMA_NAME}\".update_dependencies() RETURNS TRIGGER AS $$
                BEGIN
                PERFORM \"{config.SCHEMA_NAME}\".upd_size(OLD."id", -OLD."size");
                PERFORM \"{config.SCHEMA_NAME}\".upd_size(NEW."id", NEW."size");
                PERFORM \"{config.SCHEMA_NAME}\".upd_date(NEW."id", NEW."date", False);
                RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
                """)
            # FUNCTION delete dependencies
            local_session.execute(f"""
                CREATE OR REPLACE FUNCTION \"{config.SCHEMA_NAME}\".delete_dependencies() RETURNS TRIGGER AS $$
                BEGIN
                PERFORM \"{config.SCHEMA_NAME}\".upd_size(OLD."id", -OLD."size");
                PERFORM \"{config.SCHEMA_NAME}\".upd_date(OLD."id", OLD."date", True);
                RETURN OLD;
                END
                $$ LANGUAGE plpgsql;
                """)

    @staticmethod
    def create_trigger():
        schema_table_name_main = f"\"{config.SCHEMA_NAME}\".\"{config.TBL_SystemItem}\""
        with session(bind=engine) as local_session:
            # TRIGGER insert
            local_session.execute(f"""
                CREATE OR REPLACE TRIGGER insert_dependencies_trigger
                    AFTER INSERT ON {schema_table_name_main}
                    FOR EACH ROW
                    EXECUTE FUNCTION \"{config.SCHEMA_NAME}\".insert_dependencies();
                """)
            # TRIGGER update
            local_session.execute(f"""
                CREATE OR REPLACE TRIGGER update_dependencies_trigger
                    AFTER UPDATE ON {schema_table_name_main}
                    FOR EACH ROW
                    EXECUTE FUNCTION \"{config.SCHEMA_NAME}\".update_dependencies();
                """)
            # TRIGGER delete
            local_session.execute(f"""
                CREATE OR REPLACE TRIGGER delete_dependencies_trigger
                    BEFORE DELETE ON {schema_table_name_main}
                    FOR EACH ROW
                    EXECUTE FUNCTION \"{config.SCHEMA_NAME}\".delete_dependencies();
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
        if not engine.dialect.has_table(engine, config.TBL_SystemItemHistory) or\
                not engine.dialect.has_schema(engine, config.TBL_SystemItem):
            DataBaseSchema.create_all_tables()
            DataBaseSchema.create_functions()
            DataBaseSchema.create_trigger()


if __name__ == '__main__':
    DataBaseSchema.create_db()


