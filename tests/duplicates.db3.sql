BEGIN TRANSACTION;
DROP TABLE IF EXISTS "months";
CREATE TABLE IF NOT EXISTS "months" (
	"id"	INTEGER NOT NULL,
	"year"	INTEGER,
	"month"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "transactions";
CREATE TABLE IF NOT EXISTS "transactions" (
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
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "accounts";
CREATE TABLE IF NOT EXISTS "accounts" (
	"id"	INTEGER NOT NULL,
	"alias"	TEXT,
	"acct_routing"	TEXT,
	"acct_number"	TEXT,
	"nick_name"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "imports";
CREATE TABLE IF NOT EXISTS "imports" (
	"id"	INTEGER NOT NULL,
	"time_stamp"	TEXT DEFAULT CURRENT_TIMESTAMP,
	"source"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "duplicates";
CREATE TABLE IF NOT EXISTS "duplicates" (
	"id"	INTEGER NOT NULL,
	"transaction_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "dup_entries";
CREATE TABLE IF NOT EXISTS "dup_entries" (
	"id"	INTEGER NOT NULL,
	"duplicate_id"	INTEGER,
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
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "months" ("id","year","month") VALUES (1,2022,10),
 (2,2022,12),
 (3,2022,11),
 (4,2022,9);
INSERT INTO "transactions" ("id","account_id","month_id","import_id","import_line","date","transaction_type","customer_ref_number","amount","dc","balance","description","bank_reference") VALUES (1,1,1,1,2,'2022-10-05','Payment','',228.86,'D',1065.16,'Loan Payment to TPPL UNSECURED AND CASH SECURED',''),
 (2,1,2,1,3,'2022-12-05','Payment','',228.86,'D',107.44,'Loan Payment to TPPL UNSECURED AND CASH SECURED',''),
 (3,1,3,1,4,'2022-11-05','Payment','',228.86,'D',336.3,'Loan Payment to TPPL UNSECURED AND CASH SECURED',''),
 (4,1,3,1,5,'2022-11-04','Payment','',500.0,'D',565.16,'Bill Payment ATB Mastercard to CAD Mastercard',''),
 (5,1,4,1,8,'2022-09-26','Payment','',1260.0,'C',1294.02,'e-Transfer Received','');
INSERT INTO "accounts" ("id","alias","acct_routing","acct_number","nick_name") VALUES (1,'6789','021907339','000123456789',NULL);
INSERT INTO "imports" ("id","time_stamp","source") VALUES (1,'2023-10-24 20:36:36','./tests/duplicates_with_header.tcsv');
INSERT INTO "duplicates" ("id","transaction_id") VALUES (1,3),
 (2,1);
INSERT INTO "dup_entries" ("id","duplicate_id","account_id","month_id","import_id","import_line","date","transaction_type","customer_ref_number","amount","dc","balance","description","bank_reference") VALUES (1,1,1,3,1,6,'2022-11-05','Payment','',228.86,'D',336.3,'Loan Payment to TPPL UNSECURED AND CASH SECURED',''),
 (2,2,1,1,1,7,'2022-10-05','Payment','',228.86,'D',1065.16,'Loan Payment to TPPL UNSECURED AND CASH SECURED',''),
 (3,1,1,3,1,9,'2022-11-05','Payment','',228.86,'D',336.3,'Loan Payment to TPPL UNSECURED AND CASH SECURED','');
DROP INDEX IF EXISTS "trans_idx";
CREATE INDEX IF NOT EXISTS "trans_idx" ON "transactions" (
	"account_id",
	"date",
	"amount",
	"dc",
	"balance"
);
DROP VIEW IF EXISTS "list_dup_entries";
CREATE VIEW 'list_dup_entries'  AS 
    SELECT 
        e.id,d.id as 'duplicate_id',e.date,a.alias, a.acct_number,a.nick_name,e.transaction_type,e.customer_ref_number,
        e.amount,e.dc,e.balance,e.description, datetime(i.time_stamp, 'localtime') as 'import_time', i.source as 'import_source', e.import_line 
    FROM dup_entries e 
        INNER JOIN duplicates d ON e.duplicate_id = d.id 
        INNER JOIN accounts a ON e.account_id = a.id 
        INNER JOIN imports i ON e.import_id = i.id
    ;
DROP VIEW IF EXISTS "list_duplicates";
CREATE VIEW 'list_duplicates'  AS
    SELECT 
        d.id, t.id as transaction_id,t.date,a.alias,a.nick_name,a.acct_number,t.transaction_type,t.customer_ref_number,
        t.amount,t.dc,t.balance,t.description,
        datetime(i.time_stamp, 'localtime') as 'import_time', i.source as 'import_source', t.import_line
    FROM transactions t
        INNER JOIN duplicates d ON d.transaction_id = t.id  
        INNER JOIN accounts a ON t.account_id = a.id
        INNER JOIN imports i ON t.import_id = i.id
    WHERE
        t.id IN (SELECT transaction_id FROM duplicates);
COMMIT;
