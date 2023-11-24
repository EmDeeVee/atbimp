PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "month";
CREATE TABLE IF NOT EXISTS "month" (
	"id"	INTEGER NOT NULL,
	"month"	TEXT,
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
	"source"	TEXT NOT NULL DEFAULT '',
    "linesRead"         INTEGER NOT NULL DEFAULT 0,       -- Total number of lines in the file
    "dataLinesFound"    INTEGER NOT NULL DEFAULT 0,       -- Total number of data lines found
    "incorrectDate"     INTEGER NOT NULL DEFAULT 0,       -- Total number of lines with incorrect date
	"leadingQuote"      INTEGER NOT NULL DEFAULT 0,       -- Total number of lines with a leading quote
    "trailingComma"     INTEGER NOT NULL DEFAULT 0,       -- Total number of lines with a trailing comma
    "singleQuote"       INTEGER NOT NULL DEFAULT 0,       -- Total number of lines containing a single quote in text
    "totalErrors"       INTEGER NOT NULL DEFAULT 0,       -- Total number of errors found
    "recordsImported"   INTEGER NOT NULL DEFAULT 0,       -- Total number of records imported.
    "recordsExported"   INTEGER NOT NULL DEFAULT 0,       -- Total number of records exported.
    "sqlInsertErrors"   INTEGER NOT NULL DEFAULT 0,       -- Total number of Sql Insert Errorrs.
    "duplicatesFound"   INTEGER NOT NULL DEFAULT 0,       -- Total number of duplicates found.
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "transaction";
CREATE TABLE IF NOT EXISTS "transaction" (
	"id"	INTEGER NOT NULL,
	"account_id"	INTEGER,
	"month_id"	INTEGER,
	"import_id"	INTEGER,
	"import_line"	INTEGER,
    "flag"          TEXT DEFAULT '', -- flag this rec.  D for duplicate
    "duplicate_of" INTEGER NOT NULL DEFAULT 0,     -- If this is marked as a dup, it's a dup of ...
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

DROP INDEX IF EXISTS "trans_idx";
CREATE INDEX IF NOT EXISTS "trans_idx" ON "transaction" (
	"account_id",
	"date",
	"amount",
	"dc",
	"balance"
);

COMMIT;
