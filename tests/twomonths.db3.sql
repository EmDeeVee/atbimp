PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "month" (
	"id"	INTEGER NOT NULL,
	"month"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO month VALUES(1,'2022-12');
INSERT INTO month VALUES(2,'2022-11');
CREATE TABLE IF NOT EXISTS "account" (
	"id"	INTEGER NOT NULL,
	"alias"	TEXT,
	"acct_routing"	TEXT,
	"acct_number"	TEXT,
	"nick_name"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO account VALUES(1,'1234','021907339','000555551234','Unlimited');
INSERT INTO account VALUES(2,'7890','021907339','000555557890','Business');
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
INSERT INTO import VALUES(1,'2023-11-24 02:08:22','tests/twomonths1.tcsv',117,117,0,0,0,17,17,117,0,0,0);
INSERT INTO import VALUES(2,'2023-11-24 02:09:29','tests/twomonths2.tcsv',3,3,0,0,0,0,0,3,0,0,0);
INSERT INTO import VALUES(3,'2023-11-24 03:35:25','tests/twomonths2.tcsv',3,3,0,0,0,0,0,3,0,0,3);
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
INSERT INTO "transaction" VALUES(1,1,1,1,1,' ',0,'2022-12-31','Fee','',9.9499999999999992894,'D',3210.2899999999999637,'Monthly Maintenance Fees','');
INSERT INTO "transaction" VALUES(2,1,1,1,2,' ',0,'2022-12-31','Withdrawal','',3.9799999999999999822,'D',3220.2399999999997816,'POS Purchase CA COOP SNAKETOWN FOOD CA COOP SNAKET','');
INSERT INTO "transaction" VALUES(3,1,1,1,3,' ',0,'2022-12-31','Withdrawal','',10.75,'D',3224.2199999999997998,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(4,1,1,1,4,' ',0,'2022-12-31','Withdrawal','',35.0,'D',3234.9699999999997998,'POS Purchase SNAKETOWN LIONS SNAKETOWN LIONS','');
INSERT INTO "transaction" VALUES(5,1,1,1,5,' ',0,'2022-12-31','Withdrawal','',56.579999999999998293,'D',3269.9699999999997999,'POS Purchase THE LIQUOR HUTC THE LIQUOR HUTC','');
INSERT INTO "transaction" VALUES(6,1,1,1,6,' ',0,'2022-12-31','Withdrawal','',25.0,'D',3326.5500000000001819,'POS Purchase PETRO-CANADA PETRO-CANADA           I','');
INSERT INTO "transaction" VALUES(7,1,1,1,7,' ',0,'2022-12-30','Withdrawal','',114.71999999999999886,'D',3351.550000000000182,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(8,1,1,1,8,' ',0,'2022-12-30','Withdrawal','',36.219999999999998863,'D',3466.2699999999999817,'POS Purchase #384 SPORT CHEK #384 SPORT CHEK','');
INSERT INTO "transaction" VALUES(9,1,1,1,9,' ',0,'2022-12-30','EFT','',2272.8299999999999271,'C',3502.4899999999997816,'Direct Deposit Payroll Deposit Big Boss inc','');
INSERT INTO "transaction" VALUES(10,1,1,1,10,' ',0,'2022-12-29','EFT','',25.0,'D',1229.6600000000000818,'Direct Debit Utility Bill Payment Snake twn pmnts','');
INSERT INTO "transaction" VALUES(11,1,1,1,11,' ',0,'2022-12-29','EFT','',54.499999999999999998,'D',1254.6600000000000818,'Direct Debit Bill Payment Koodo Mobile','');
INSERT INTO "transaction" VALUES(12,1,1,1,12,' ',0,'2022-12-29','Withdrawal','',69.540000000000006252,'D',1309.1600000000000818,'POS Purchase PHARMASAVE #327 PHARMASAVE #327','');
INSERT INTO "transaction" VALUES(13,1,1,1,13,' ',0,'2022-12-28','Withdrawal','',202.63999999999998636,'D',1378.7000000000000454,'POS Purchase CANADIAN TIRE # CANADIAN TIRE #','');
INSERT INTO "transaction" VALUES(14,1,1,1,14,' ',0,'2022-12-28','Payment','',1500.0,'C',1581.339999999999918,'e-Transfer Received','');
INSERT INTO "transaction" VALUES(15,1,1,1,15,' ',0,'2022-12-24','Withdrawal','',67.689999999999997727,'D',81.34000000000000341,'POS Purchase CA COOP SNAKETWN CA COOP SNAKETWN','');
INSERT INTO "transaction" VALUES(16,1,1,1,16,' ',0,'2022-12-24','Withdrawal','',65.579999999999998294,'D',149.03000000000000114,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(17,1,1,1,17,' ',0,'2022-12-23','EFT','',22.039999999999999146,'D',214.61000000000001364,'Direct Debit Misc. Payments PAYPAL','');
INSERT INTO "transaction" VALUES(18,1,1,1,18,' ',0,'2022-12-22','Withdrawal','',1.9199999999999999289,'D',236.65000000000000568,'POS Purchase TIM HORTONS #25 TIM HORTONS #25','');
INSERT INTO "transaction" VALUES(19,1,1,1,19,' ',0,'2022-12-22','Withdrawal','',7.0,'D',238.56999999999999317,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(20,1,1,1,20,' ',0,'2022-12-21','Withdrawal','',29.649999999999998578,'D',245.56999999999999317,'POS Purchase THE HOME DEPOT THE HOME DEPOT','');
INSERT INTO "transaction" VALUES(21,1,1,1,21,' ',0,'2022-12-21','Withdrawal','',4.2199999999999997513,'D',275.22000000000002729,'POS Purchase TIM HORTONS #25 TIM HORTONS #25','');
INSERT INTO "transaction" VALUES(22,1,1,1,22,' ',0,'2022-12-20','EFT','',160.83000000000001249,'D',279.43999999999999772,'Direct Debit Utility Bill Payment Enmax','');
INSERT INTO "transaction" VALUES(23,1,1,1,23,' ',0,'2022-12-20','EFT','',255.56999999999999318,'D',440.2699999999999818,'Direct Debit Insurance AB Blue Cross','');
INSERT INTO "transaction" VALUES(24,1,1,1,24,' ',0,'2022-12-20','Withdrawal','',7.330000000000000071,'D',695.84000000000003184,'POS Purchase THE HOME DEPOT THE HOME DEPOT','');
INSERT INTO "transaction" VALUES(25,1,1,1,25,' ',0,'2022-12-20','Withdrawal','',35.640000000000000568,'D',703.16999999999995909,'POS Purchase BOB''S TAG SHOPPE BOB''S TAG SHOP','');
INSERT INTO "transaction" VALUES(26,1,1,1,26,' ',0,'2022-12-20','Withdrawal','',20.30999999999999872,'D',738.8099999999999454,'POS Purchase TIM HORTONS #2525 TIM HORTONS #2525','');
INSERT INTO "transaction" VALUES(27,1,1,1,27,' ',0,'2022-12-20','Payment','',300.0,'D',759.12000000000000453,'Bill Payment ATB Mastercard to CAD Mastercard','');
INSERT INTO "transaction" VALUES(28,1,1,1,28,' ',0,'2022-12-18','Withdrawal','',8.9700000000000006394,'D',1059.1199999999998908,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(29,1,1,1,29,' ',0,'2022-12-18','Withdrawal','',6.2999999999999998223,'D',1068.0899999999999181,'POS Purchase DOLLARAMA #1372 DOLLARAMA #1372','');
INSERT INTO "transaction" VALUES(30,1,1,1,30,' ',0,'2022-12-18','Withdrawal','',26.769999999999999572,'D',1074.3900000000001,'POS Purchase SNAKETOWN AQUAT SNAKETOWN AQUAT','');
INSERT INTO "transaction" VALUES(31,1,1,1,31,' ',0,'2022-12-17','Withdrawal','',7.8600000000000003197,'D',1101.1600000000000818,'POS Purchase CA COOP SNAKETWN CA COOP SNAKETWN','');
INSERT INTO "transaction" VALUES(32,1,1,1,32,' ',0,'2022-12-16','EFT','',81.950000000000002842,'D',1109.0199999999999818,'Direct Debit Telephone Bill Payment FIDO MOBILE','');
INSERT INTO "transaction" VALUES(33,1,1,1,33,' ',0,'2022-12-16','Withdrawal','',46.34000000000000341,'D',1190.9700000000000273,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(34,1,1,1,34,' ',0,'2022-12-15','Withdrawal','',232.31000000000000228,'D',1237.3099999999999454,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(35,1,1,1,35,' ',0,'2022-12-15','Withdrawal','',31.120000000000000994,'D',1469.6199999999998908,'POS Purchase LONDON DRUGS 24 LONDON DRUGS 24','');
INSERT INTO "transaction" VALUES(36,1,1,1,36,' ',0,'2022-12-14','Withdrawal','',20.010000000000001563,'D',1500.740000000000009,'POS Purchase PETRO-CANADA PETRO-CANADA           R','');
INSERT INTO "transaction" VALUES(37,1,1,1,37,' ',0,'2022-12-14','Withdrawal','',23.089999999999999858,'D',1520.7499999999999999,'POS Purchase COSTCO WHOLESAL COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(38,1,1,1,38,' ',0,'2022-12-13','Withdrawal','',3.4100000000000001421,'D',1543.839999999999918,'POS Purchase STARBUCKS # 961 STARBUCKS # 961','');
INSERT INTO "transaction" VALUES(39,1,1,1,39,' ',0,'2022-12-12','EFT','',98.75,'D',1547.2499999999999999,'Direct Debit Bill Payment Telme Comm','');
INSERT INTO "transaction" VALUES(40,1,1,1,40,' ',0,'2022-12-11','Withdrawal','',8.9000000000000003552,'D',1646.0,'POS Purchase DAIRY QUEEN #27 DAIRY QUEEN #27','');
INSERT INTO "transaction" VALUES(41,1,1,1,41,' ',0,'2022-12-11','Withdrawal','',50.0,'D',1654.900000000000091,'POS Purchase WESTVIEW CO-OP QE 2 GB WESTVIEW CO-OP','');
INSERT INTO "transaction" VALUES(42,1,1,1,42,' ',0,'2022-12-11','Withdrawal','',6.5899999999999998578,'D',1704.9000000000000909,'POS Purchase FGP40012 DIDSBU FGP40012 DIDSBU','');
INSERT INTO "transaction" VALUES(43,1,1,1,43,' ',0,'2022-12-11','Withdrawal','',33.140000000000000568,'D',1711.4900000000000091,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(44,1,1,1,44,' ',0,'2022-12-10','Payment','',40.0,'D',1744.6300000000001091,'Bill Payment to CIBC  Mastercard','');
INSERT INTO "transaction" VALUES(45,1,1,1,45,' ',0,'2022-12-10','Payment','',500.0,'D',1784.6300000000001091,'Bill Payment ATB Mastercard to CAD Mastercard','');
INSERT INTO "transaction" VALUES(46,1,1,1,46,' ',0,'2022-12-10','Withdrawal','',27.079999999999998295,'D',2284.630000000000109,'POS Purchase PHARMASAVE #327 PHARMASAVE #327','');
INSERT INTO "transaction" VALUES(47,1,1,1,47,' ',0,'2022-12-10','Withdrawal','',45.0,'D',2311.7100000000000363,'POS Purchase PETRO-CANADA PETRO-CANADA           I','');
INSERT INTO "transaction" VALUES(48,1,1,1,48,' ',0,'2022-12-09','EFT','',11.539999999999999147,'D',2356.7100000000000363,'Direct Debit Misc. Payments PAYPAL','');
INSERT INTO "transaction" VALUES(49,1,1,1,49,' ',0,'2022-12-09','Withdrawal','',29.44999999999999929,'D',2368.25,'POS Purchase PETRO-CANADA PETRO-CANADA           R','');
INSERT INTO "transaction" VALUES(50,1,1,1,50,' ',0,'2022-12-08','Withdrawal','',19.760000000000001563,'D',2397.6999999999998181,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(51,1,1,1,51,' ',0,'2022-12-08','Withdrawal','',23.600000000000001421,'D',2417.4600000000000363,'POS Purchase MICHAELS #3910 MICHAELS #3910','');
INSERT INTO "transaction" VALUES(52,1,1,1,52,' ',0,'2022-12-08','Withdrawal','',11.980000000000000426,'D',2441.0599999999999453,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(53,1,1,1,53,' ',0,'2022-12-07','Withdrawal','',48.969999999999998863,'D',2453.0399999999999635,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(54,1,1,1,54,' ',0,'2022-12-07','Withdrawal','',49.039999999999999147,'D',2502.0100000000002182,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(55,1,1,1,55,' ',0,'2022-12-07','Withdrawal','',28.620000000000000994,'D',2551.0500000000001818,'POS Purchase PETRO-CANADA PETRO-CANADA           I','');
INSERT INTO "transaction" VALUES(56,1,1,1,56,' ',0,'2022-12-04','Withdrawal','',6.5999999999999996447,'D',2579.6700000000000727,'POS Purchase INDUS RECREATIO INDUS RECREATIO','');
INSERT INTO "transaction" VALUES(57,1,1,1,57,' ',0,'2022-12-02','Withdrawal','',178.52000000000001023,'D',2586.2699999999999818,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(58,1,1,1,58,' ',0,'2022-12-02','Withdrawal','',129.0099999999999909,'D',2764.7899999999999635,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(59,1,1,1,59,' ',0,'2022-12-02','Transfer','',500.0,'D',2893.8000000000001818,'Transfer to BUDDY JO','');
INSERT INTO "transaction" VALUES(60,1,1,1,60,' ',0,'2022-12-01','EFT','',1729.4800000000000181,'D',3393.8000000000001818,'Direct Debit Mortgage Hello World Bank','');
INSERT INTO "transaction" VALUES(61,1,1,1,61,' ',0,'2022-12-01','EFT','',414.97000000000002729,'D',5123.2799999999997452,'Direct Debit Insurance INTACT INS. CO.','');
INSERT INTO "transaction" VALUES(62,1,1,1,62,' ',0,'2022-12-01','EFT','',117.99999999999999999,'D',5538.2500000000000001,'Direct Debit Insurance NON-GROUP','');
INSERT INTO "transaction" VALUES(63,1,1,1,63,' ',0,'2022-12-01','Withdrawal','',99.930000000000006824,'D',5656.25,'POS Purchase UFA SNAKETOWN C/L   #2 UFA SNAKETOWN','');
INSERT INTO "transaction" VALUES(64,1,1,1,64,' ',0,'2022-12-01','EFT','',1305.4000000000000909,'C',5756.1800000000002911,'Direct Deposit Payroll Deposit Big Boss inc','');
INSERT INTO "transaction" VALUES(65,1,2,1,65,' ',0,'2022-11-30','Fee','',9.9499999999999992894,'D',4450.7799999999997451,'Monthly Maintenance Fees','');
INSERT INTO "transaction" VALUES(66,1,2,1,66,' ',0,'2022-11-30','Transfer','',0.010000000000000000208,'D',4460.7299999999995634,'Overdraft Interest','');
INSERT INTO "transaction" VALUES(67,1,2,1,67,' ',0,'2022-11-30','Withdrawal','',51.369999999999997443,'D',4460.7399999999997816,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(68,1,2,1,68,' ',0,'2022-11-30','Withdrawal','',20.010000000000001563,'D',4512.1099999999996726,'POS Purchase PETRO-CANADA PETRO-CANADA           R','');
INSERT INTO "transaction" VALUES(69,1,2,1,69,' ',0,'2022-11-30','Payment','',4000.0,'C',4532.1199999999998908,'e-Transfer Received','');
INSERT INTO "transaction" VALUES(70,1,2,1,70,' ',0,'2022-11-29','Withdrawal','',42.030000000000001135,'D',532.12000000000000453,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(71,1,2,1,71,' ',0,'2022-11-28','EFT','',54.499999999999999998,'D',574.14999999999997725,'Direct Debit Bill Payment Koodo Mobile','');
INSERT INTO "transaction" VALUES(72,1,2,1,72,' ',0,'2022-11-28','EFT','',25.0,'D',628.64999999999997726,'Direct Debit Utility Bill Payment T of Inn pmnts','');
INSERT INTO "transaction" VALUES(73,1,2,1,73,' ',0,'2022-11-28','Withdrawal','',3.2599999999999997868,'D',653.64999999999997726,'POS Purchase LONDON DRUGS 24 LONDON DRUGS 24','');
INSERT INTO "transaction" VALUES(74,1,2,1,74,' ',0,'2022-11-27','Withdrawal','',6.25,'D',656.90999999999996816,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(75,1,2,1,75,' ',0,'2022-11-26','Withdrawal','',23.929999999999999715,'D',663.15999999999996816,'POS Purchase PHARMASAVE #327 PHARMASAVE #327','');
INSERT INTO "transaction" VALUES(76,1,2,1,76,' ',0,'2022-11-24','Payment','',300.0,'D',687.09000000000003184,'Bill Payment ATB Mastercard to CAD Mastercard','');
INSERT INTO "transaction" VALUES(77,1,2,1,77,' ',0,'2022-11-24','Payment','',1000.0,'C',987.09000000000003179,'e-Transfer Received','');
INSERT INTO "transaction" VALUES(78,1,2,1,78,' ',0,'2022-11-23','EFT','',22.039999999999999146,'D',-12.910000000000000141,'Direct Debit Misc. Payments PAYPAL','');
INSERT INTO "transaction" VALUES(79,1,2,1,79,' ',0,'2022-11-23','Withdrawal','',14.859999999999999431,'D',9.1300000000000007815,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(80,1,2,1,80,' ',0,'2022-11-23','Withdrawal','',8.1699999999999999289,'D',23.989999999999998437,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(81,1,2,1,81,' ',0,'2022-11-22','EFT','',170.21999999999999886,'D',32.159999999999996588,'Direct Debit Utility Bill Payment Enmax','');
INSERT INTO "transaction" VALUES(82,1,2,1,82,' ',0,'2022-11-22','Withdrawal','',56.689999999999997727,'D',202.37999999999999544,'POS Purchase WALMART STORE #1084 WALMART STORE #10','');
INSERT INTO "transaction" VALUES(83,1,2,1,83,' ',0,'2022-11-21','EFT','',255.56999999999999318,'D',259.06999999999999317,'Direct Debit Insurance AB Blue Cross','');
INSERT INTO "transaction" VALUES(84,1,2,1,84,' ',0,'2022-11-17','Transfer','',500.0,'C',514.63999999999998635,'Transfer from BUDDY JO','');
INSERT INTO "transaction" VALUES(85,1,2,1,85,' ',0,'2022-11-17','Withdrawal','',143.5099999999999909,'D',14.640000000000000568,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(86,1,2,1,86,' ',0,'2022-11-17','Withdrawal','',77.980000000000003978,'D',158.15000000000000568,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(87,1,2,1,87,' ',0,'2022-11-16','EFT','',81.950000000000002842,'D',236.12999999999999545,'Direct Debit Telephone Bill Payment FIDO MOBILE','');
INSERT INTO "transaction" VALUES(88,1,2,1,88,' ',0,'2022-11-16','Withdrawal','',100.0,'D',318.07999999999998408,'Withdrawal ABM 4962 50TH STREET Innisfail','');
INSERT INTO "transaction" VALUES(89,1,2,1,89,' ',0,'2022-11-15','Withdrawal','',3.4100000000000001421,'D',418.0799999999999841,'POS Purchase STARBUCKS # 961 STARBUCKS # 961','');
INSERT INTO "transaction" VALUES(90,1,2,1,90,' ',0,'2022-11-14','EFT','',53.90999999999999659,'D',421.49000000000000909,'Direct Debit Misc. Payments PAYPAL','');
INSERT INTO "transaction" VALUES(91,1,2,1,91,' ',0,'2022-11-14','Withdrawal','',15.849999999999999644,'D',475.39999999999997728,'POS Purchase JOHN''S NO FRILL JOHN''S NO FRILL','');
INSERT INTO "transaction" VALUES(92,1,2,1,92,' ',0,'2022-11-14','Withdrawal','',3.4100000000000001421,'D',491.24999999999999999,'POS Purchase STARBUCKS # 961 STARBUCKS # 961','');
INSERT INTO "transaction" VALUES(93,1,2,1,93,' ',0,'2022-11-11','Withdrawal','',48.189999999999997724,'D',494.66000000000002502,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(94,1,2,1,94,' ',0,'2022-11-11','Withdrawal','',224.49000000000000909,'D',542.85000000000002274,'POS Purchase COSTCO WHOLESALE W164 COSTCO WHOLESAL','');
INSERT INTO "transaction" VALUES(95,1,2,1,95,' ',0,'2022-11-11','Withdrawal','',7.1299999999999998934,'D',767.34000000000003182,'POS Purchase CA COOP SNAKETWN CA COOP SNAKETWN','');
INSERT INTO "transaction" VALUES(96,1,2,1,96,' ',0,'2022-11-11','Withdrawal','',17.329999999999998294,'D',774.47000000000002727,'POS Purchase CA COOP SNAKETWN CA COOP SNAKETWN','');
INSERT INTO "transaction" VALUES(97,1,2,1,97,' ',0,'2022-11-10','Withdrawal','',19.940000000000001278,'D',791.7999999999999545,'POS Purchase SANDSTONE PHARM SANDSTONE PHARM','');
INSERT INTO "transaction" VALUES(98,1,2,1,98,' ',0,'2022-11-09','EFT','',98.75,'D',811.7400000000000091,'Direct Debit Bill Payment Telme Comm','');
INSERT INTO "transaction" VALUES(99,1,2,1,99,' ',0,'2022-11-09','Withdrawal','',44.950000000000002843,'D',910.49000000000000912,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(100,1,2,1,100,' ',0,'2022-11-09','Withdrawal','',4.2199999999999997513,'D',955.4400000000000546,'POS Purchase TIM HORTONS #25 TIM HORTONS #25','');
INSERT INTO "transaction" VALUES(101,1,2,1,101,' ',0,'2022-11-08','Withdrawal','',10.640000000000000568,'D',959.65999999999996817,'POS Purchase 7 DAYS LIQUOR S 7 DAYS LIQUOR S','');
INSERT INTO "transaction" VALUES(102,1,2,1,102,' ',0,'2022-11-08','Withdrawal','',64.250000000000000001,'D',970.29999999999995453,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(103,1,2,1,103,' ',0,'2022-11-07','Withdrawal','',15.0,'D',1034.5499999999999545,'POS Purchase PETRO-CANADA PETRO-CANADA           I','');
INSERT INTO "transaction" VALUES(104,1,2,1,104,' ',0,'2022-11-07','Withdrawal','',1.9199999999999999289,'D',1049.5499999999999545,'POS Purchase TIM HORTONS #25 TIM HORTONS #25','');
INSERT INTO "transaction" VALUES(105,1,2,1,105,' ',0,'2022-11-06','Withdrawal','',61.810000000000002275,'D',1051.4700000000000272,'POS Purchase WALMART STORE # WALMART STORE #','');
INSERT INTO "transaction" VALUES(106,1,2,1,106,' ',0,'2022-11-04','Withdrawal','',166.56999999999999317,'D',1113.2799999999999727,'POS Purchase WALMART STORE #5217 WALMART STORE #31','');
INSERT INTO "transaction" VALUES(107,1,2,1,107,' ',0,'2022-11-04','Payment','',500.0,'D',1279.849999999999909,'Bill Payment ATB Mastercard to CAD Mastercard','');
INSERT INTO "transaction" VALUES(108,1,2,1,108,' ',0,'2022-11-04','Payment','',1500.0,'C',1779.849999999999909,'e-Transfer Received','');
INSERT INTO "transaction" VALUES(109,1,2,1,109,' ',0,'2022-11-04','Withdrawal','',18.890000000000000568,'D',279.85000000000002273,'POS Purchase PETRO-CANADA PETRO-CANADA           I','');
INSERT INTO "transaction" VALUES(110,1,2,1,110,' ',0,'2022-11-03','Withdrawal','',42.679999999999999717,'D',298.74000000000000909,'POS Purchase JOHN''S NO FRILLS # 821 JOHN''S NO FRIL','');
INSERT INTO "transaction" VALUES(111,1,2,1,111,' ',0,'2022-11-03','Withdrawal','',4.4599999999999999644,'D',341.42000000000001591,'POS Purchase STARBUCKS # 961 STARBUCKS # 961','');
INSERT INTO "transaction" VALUES(112,1,2,1,112,' ',0,'2022-11-03','Withdrawal','',3.0,'D',345.87999999999999546,'POS Purchase MCDONALD''S #584 MCDONALD''S #584','');
INSERT INTO "transaction" VALUES(113,1,2,1,113,' ',0,'2022-11-01','EFT','',117.99999999999999999,'D',348.87999999999999545,'Direct Debit Insurance NON-GROUP','');
INSERT INTO "transaction" VALUES(114,1,2,1,114,' ',0,'2022-11-01','EFT','',1729.4800000000000181,'D',466.87999999999999544,'Direct Debit Mortgage Hello World Bank','');
INSERT INTO "transaction" VALUES(115,1,2,1,115,' ',0,'2022-11-01','EFT','',414.97000000000002729,'D',2196.3600000000001273,'Direct Debit Insurance INTACT INS. CO.','');
INSERT INTO "transaction" VALUES(116,1,2,1,116,' ',0,'2022-11-01','Withdrawal','',1103.3199999999999363,'D',2611.3299999999999272,'POS Purchase BEST BUY #960 BEST BUY #960','');
INSERT INTO "transaction" VALUES(117,1,2,1,117,' ',0,'2022-11-01','Transfer','',1299.9999999999999999,'C',3714.6500000000000909,'Transfer from BUDDY JO','');
INSERT INTO "transaction" VALUES(118,2,1,2,1,' ',0,'2022-12-05','Payment','',228.86000000000001363,'D',107.43999999999999772,'Loan Payment to TPPL UNSECURED AND CASH SECURED','');
INSERT INTO "transaction" VALUES(119,2,2,2,2,' ',0,'2022-11-05','Payment','',228.86000000000001363,'D',336.30000000000001135,'Loan Payment to TPPL UNSECURED AND CASH SECURED','');
INSERT INTO "transaction" VALUES(120,2,2,2,3,' ',0,'2022-11-04','Payment','',500.0,'D',565.15999999999996816,'Bill Payment ATB Mastercard to CAD Mastercard','');
INSERT INTO "transaction" VALUES(121,2,1,3,1,'D',118,'2022-12-05','Payment','',228.86000000000001363,'D',107.43999999999999772,'Loan Payment to TPPL UNSECURED AND CASH SECURED','');
INSERT INTO "transaction" VALUES(122,2,2,3,2,'D',119,'2022-11-05','Payment','',228.86000000000001363,'D',336.30000000000001135,'Loan Payment to TPPL UNSECURED AND CASH SECURED','');
INSERT INTO "transaction" VALUES(123,2,2,3,3,'D',120,'2022-11-04','Payment','',500.0,'D',565.15999999999996816,'Bill Payment ATB Mastercard to CAD Mastercard','');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('import',3);
INSERT INTO sqlite_sequence VALUES('account',2);
INSERT INTO sqlite_sequence VALUES('month',2);
INSERT INTO sqlite_sequence VALUES('transaction',123);
CREATE INDEX "trans_idx" ON "transaction" (
	"account_id",
	"date",
	"amount",
	"dc",
	"balance"
);
COMMIT;
