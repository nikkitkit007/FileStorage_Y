# FUNCTION update size
```
CREATE OR REPLACE FUNCTION "ItemStorage".upd_size(id_add_item varchar, change_size integer) RETURNS INTEGER AS $$
BEGIN
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
RETURN NULL;
END
$$ LANGUAGE plpgsql;
```
# FUNCTION update date
```
CREATE OR REPLACE FUNCTION "ItemStorage".upd_date(id_add_item varchar, date_upd timestamp) RETURNS INTEGER AS $$
BEGIN
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
	SET "date" = date_upd
	WHERE "ItemStorage"."SystemItem"."id"
	in (SELECT "parentId" FROM r);
RETURN NULL;
END
$$ LANGUAGE plpgsql;
```

# TRIGGER insert
```
CREATE OR REPLACE TRIGGER insert_dependencies_trigger
    AFTER INSERT ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".insert_dependencies();
```
# TRIGGER update
```
CREATE OR REPLACE TRIGGER update_dependencies_trigger
    AFTER UPDATE ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".update_dependencies();
```
# TRIGGER delete
```
CREATE OR REPLACE TRIGGER delete_dependencies_trigger
    AFTER DELETE ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".delete_dependencies();
```
# FUNCTION insert_dependencies
```
CREATE OR REPLACE FUNCTION "ItemStorage".insert_dependencies() RETURNS TRIGGER AS $$
BEGIN
PERFORM "ItemStorage".upd_size(NEW."id", NEW."size");
PERFORM "ItemStorage".upd_date(NEW."id", NEW."date");
RETURN NEW;
END
$$ LANGUAGE plpgsql;
```
# FUNCTION update_dependencies
```
CREATE OR REPLACE FUNCTION "ItemStorage".update_dependencies() RETURNS TRIGGER AS $$
BEGIN
PERFORM "ItemStorage".upd_size(OLD."id", -OLD."size");
PERFORM "ItemStorage".upd_size(NEW."id", NEW."size");
PERFORM "ItemStorage".upd_date(NEW."id", NEW."date");
RETURN NEW;
END
$$ LANGUAGE plpgsql;
```
# FUNCTION delete_dependencies
```
CREATE OR REPLACE FUNCTION "ItemStorage".delete_dependencies() RETURNS TRIGGER AS $$
BEGIN
PERFORM "ItemStorage".upd_size(OLD."id", -OLD."size");
PERFORM "ItemStorage".upd_date(OLD."id", OLD."date");
RETURN OLD;
END
$$ LANGUAGE plpgsql;
```