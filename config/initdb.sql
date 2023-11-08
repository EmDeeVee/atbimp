PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "month";
CREATE TABLE IF NOT EXISTS "month" (
	"id"	INTEGER NOT NULL,
	"year"	INTEGER,
	"month"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "account";
CREATE TABLE IF NOT EXISTS "account" (
	"id"	INTEGER NOT NULL,
	"alias"	TEXT,
	"acct_routing"	TEXT,
	"acct_number"	TEXT,
	"nick_name"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "import";
CREATE TABLE IF NOT EXISTS "import" (
	"id"	INTEGER NOT NULL,
	"time_stamp"	TEXT DEFAULT CURRENT_TIMESTAMP,
	"source"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "transaction";
CREATE TABLE IF NOT EXISTS "transaction" (
	"id"	INTEGER NOT NULL,
	"account_id"	INTEGER,
	"month_id"	INTEGER,
	"import_id"	INTEGER,
	"import_line"	INTEGER,
	"date"	TEXT,
	"transaction_type"	TEXT,
	"customer_ref_number"	TEXT,
	"amount"	REAL,
	"dc"	TEXT,
	"balance"	REAL,
	"description"	TEXT,
	"bank_reference"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("account_id") REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY("month_id") REFERENCES month(id) ON DELETE CASCADE,
    FOREIGN KEY("import_id") REFERENCES import(id) ON DELETE CASCADE
);
DROP TABLE IF EXISTS "duplicate";
CREATE TABLE IF NOT EXISTS "duplicate" (
	"id"	INTEGER NOT NULL,
	"transaction_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "duplicate_entry";
CREATE TABLE IF NOT EXISTS "duplicate_entry" (
	"id"	INTEGER NOT NULL,
	"duplicate_id"	INTEGER,
	"import_id"	INTEGER,
	"import_line"	INTEGER,
	"date"	TEXT,
	"transaction_type"	TEXT,
	"customer_ref_number"	TEXT,
	"amount"	REAL,
	"dc"	TEXT,
	"balance"	REAL,
	"description"	TEXT,
	"bank_reference"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("duplicate_id") REFERENCES duplicate(id) ON DELETE CASCADE,
    FOREIGN KEY("import_id") REFERENCES import(id) ON DELETE CASCADE
);
DROP INDEX IF EXISTS "trans_idx";
CREATE INDEX IF NOT EXISTS "trans_idx" ON "transaction" (
	"account_id",
	"date",
	"amount",
	"dc",
	"balance"
);

DROP VIEW IF EXISTS "list_duplicate";
CREATE VIEW 'list_duplicate'  AS 
    SELECT d.id,t.id as 'transaction_id',a.id as 'account_id', t.date,a.alias,a.nick_name,a.acct_number,
        t.transaction_type,t.customer_ref_number, t.amount,t.dc,t.balance,
        t.description, datetime(i.time_stamp, 'localtime') as 'import_time', 
        i.source as 'import_source', t.import_line 
    FROM "transaction" t 
        INNER JOIN duplicate d ON d.transaction_id = t.id 
        INNER JOIN account a ON t.account_id = a.id 
        INNER JOIN import i ON t.import_id = i.id 
    WHERE t.id IN (SELECT transaction_id FROM duplicate);
    
DROP VIEW IF EXISTS "list_duplicate_entry";
CREATE VIEW 'list_duplicate_entry'  AS 
    SELECT e.id,d.id as 'duplicate_id',e.date,a.alias, a.acct_number,a.nick_name,
        e.transaction_type,e.customer_ref_number, e.amount,e.dc,e.balance,e.description, 
        datetime(i.time_stamp, 'localtime') as 'import_time', i.source as 'import_source', 
        e.import_line 
    FROM duplicate_entry e 
        INNER JOIN import i ON e.import_id = i.id
        INNER JOIN duplicate d ON e.duplicate_id = d.id 
        INNER JOIN "transaction" t ON t.id = d.transaction_id
        INNER JOIN account a ON a.id  = t.account_id
    ;
COMMIT;
