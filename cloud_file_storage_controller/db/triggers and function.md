

```
CREATE OR REPLACE TRIGGER change_size_parent
    AFTER INSERT ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".add_size();
```

```
CREATE OR REPLACE FUNCTION "ItemStorage".add_size(id_add_item varchar, change_size integer) RETURNS INTEGER AS $$
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

```
CREATE OR REPLACE FUNCTION "ItemStorage".insert_add_size() RETURNS TRIGGER AS $$
BEGIN
EXECUTE FUNCTION "ItemStorage".add_size(NEW."id", NEW."size");
RETURN NULL;
END
$$ LANGUAGE plpgsql;
```

# trigger
```
CREATE OR REPLACE TRIGGER change_size_parent
    AFTER INSERT ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".insert_add_size();


```

# FUNCTION "ItemStorage".insert_add_size()
```
CREATE OR REPLACE FUNCTION "ItemStorage".insert_add_size() RETURNS TRIGGER AS $$
BEGIN
PERFORM "ItemStorage".add_size(NEW."id", NEW."size");
RETURN NEW;
END
$$ LANGUAGE plpgsql;
```

# FUNCTION "ItemStorage".insert_del_size()
```
CREATE OR REPLACE FUNCTION "ItemStorage".insert_del_size() RETURNS TRIGGER AS $$
BEGIN
PERFORM "ItemStorage".add_size(OLD."id", -OLD."size");
RETURN OLD;
END
$$ LANGUAGE plpgsql;
```

# TRIGGER change_size_parent_del
```
CREATE OR REPLACE TRIGGER change_size_parent_del
    BEFORE DELETE ON "ItemStorage"."SystemItem"
	FOR EACH ROW
    EXECUTE FUNCTION "ItemStorage".insert_del_size();

```