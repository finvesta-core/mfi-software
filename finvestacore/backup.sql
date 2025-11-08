BEGIN TRANSACTION;
CREATE TABLE bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                balance REAL DEFAULT 0,
                description TEXT
            );
CREATE TABLE borrowings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outstanding_amount REAL,
                due_date DATE,
                description TEXT
            );
CREATE TABLE capital_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                description TEXT
            );
INSERT INTO "capital_accounts" VALUES(1,50000.0,'Share Capital');
CREATE TABLE cash_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('inflow', 'outflow')),
    description TEXT,
    account_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE counters (
                name TEXT PRIMARY KEY,
                last_id INTEGER DEFAULT 0
            );
INSERT INTO "counters" VALUES('members',14);
INSERT INTO "counters" VALUES('loans',2);
CREATE TABLE cumulative_pnl (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_end DATE,
                interest_amount REAL,
                expense_amount REAL
            );
CREATE TABLE deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposit_date DATE,
                type TEXT,
                amount REAL,
                description TEXT
            );
INSERT INTO "deposits" VALUES(1,'2025-04-05','cash_deposit',22400.0,'');
CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                category TEXT,
                amount REAL,
                description TEXT
            );
CREATE TABLE fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fee_date DATE,
                amount REAL,
                description TEXT
            );
CREATE TABLE investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                type TEXT,
                amount REAL,
                description TEXT
            , payment_mode TEXT DEFAULT 'UPI');
INSERT INTO "investments" VALUES(3,'2024-10-01','capital',100000.0,'','UPI');
CREATE TABLE loans (
                loan_id TEXT PRIMARY KEY,
                member_id TEXT,
                loan_type TEXT,
                amount REAL,
                purpose TEXT,
                tenure_months INTEGER,
                tenure_days INTEGER,
                interest_rate REAL,
                emi REAL,
                repayment_type TEXT,
                guarantor_id TEXT,
                status TEXT DEFAULT 'Pending',
                date_issued TEXT,
                loan_date TEXT,
                payment_mode TEXT,
                ref_id TEXT,
                emi_start_date TEXT,
                emi_end_date TEXT
            , total_paid REAL DEFAULT 0, due_amount REAL, loan_closed_date TEXT, emi_type TEXT);
INSERT INTO "loans" VALUES('PL0001','M0001','Personal',20000.0,'',NULL,120,NULL,200.0,'daily','','Closed','2025-10-24','2024-12-02','NEFT','','2024-12-03','2025-04-02',22400.0,0.0,'2025-10-26','daily');
INSERT INTO "loans" VALUES('PL0002','M0008','Personal',10000.0,'',NULL,120,NULL,100.0,'daily','','Closed','2025-10-27','2024-12-19','Cash',NULL,'2024-12-21','2025-04-20',12000.0,0.0,'2025-10-28','daily');
CREATE TABLE members (
                id TEXT PRIMARY KEY,
                date_joined TEXT,
                full_name TEXT NOT NULL,
                father_name TEXT,
                gender TEXT,
                dob TEXT,
                marital_status TEXT,
                spouse_name TEXT,
                phone_number TEXT UNIQUE NOT NULL,
                address TEXT,
                pincode TEXT,
                district TEXT,
                state TEXT,
                aadhaar TEXT UNIQUE,
                pan TEXT UNIQUE,
                ifsc TEXT,
                account_number TEXT,
                bank_branch TEXT,
                bank_address TEXT,
                guarantor_name TEXT,
                guarantor_mobile TEXT,
                guarantor_address TEXT
            , education TEXT, occupation TEXT, nominee_dob TEXT, nominee_age TEXT, nominee_name TEXT NOT NULL DEFAULT "", nominee_relation TEXT NOT NULL DEFAULT "", guarantor_relation TEXT NOT NULL DEFAULT "");
INSERT INTO "members" VALUES('M0001','2025-10-11','Ashu','Rathore','Male','1980-01-01','Single',NULL,'9837215292','budaun','243601','Unknown','Unspecified','112211221122','ABCDE1111F','SBIN0000623','112211','Location Details: District: Unknown','Unknown','RAMAN','8755881010','budaun',NULL,NULL,NULL,NULL,'','','');
INSERT INTO "members" VALUES('M0002','2025-10-14','RANJANA RATHORE','YOGENDRA KUMAR','Female','1980-06-17','Married','YOGENDRA KUMAR','7251007349','DATAGANJ TIRAHA NEAR WATER TANK BUDAUN','243601','BUDAUN','UTTAR PRADESH','923981147166','CQPPR2692E','SBIN0003555','33067890376','STATE BANK OF INDIA','BUDAUN CITY BUDAUN','ARVIND KUMAR SINGH','9836626377','JAWAHARPURI BUDAUN',NULL,NULL,NULL,NULL,'','','');
INSERT INTO "members" VALUES('M0005','2025-10-17','GUDDI','SALIM','Female','1982-01-01','Married',NULL,'8954661917','KATRA BRAHAMPUR, BUDAUN','243601','BUDAUN','UTTAR PRADESH','375996154908','EJEPG3386Q','PSIB0021471','14711000001518','PUNJAB & SINDH BANK, BUDAUN','BUDAUN','TASLIM','9105299282','KATRA BRAHAMPUR BUDAUN','Illiterate','HOUSE WIFE',NULL,NULL,'TASLIM','Child','Relative');
INSERT INTO "members" VALUES('M0006','2025-10-23','madina',NULL,'Female','1989-01-01','Married',NULL,'9258052226','atik mohalla khandsari budaun','243601','Budaun','up','838602004419',NULL,'SBIN0005310','34436748299','state bank of india','budaun','islam','7456970455','budaun','Illiterate','maid',NULL,NULL,'atik','Spouse','Relative');
INSERT INTO "members" VALUES('M0007','2025-10-23','pravesh','vikram singh','Male','1997-01-01','Married',NULL,'6395653417','vikram singh sarva majra uatrna gulariya budaun','243601','Budaun','UP','400160118642','ERHPP3039N','HDFC0002620','50100561351528','hdfc bank','budaun','raman patel','8755881010','lohiya nager budaun','Primary','auto driver',NULL,NULL,'vikram singh','Parent','Friend');
INSERT INTO "members" VALUES('M0008','2025-10-27','ARJUN RATHORE','VED','Male','1990-01-01','Single',NULL,'7251007348','JAWAHARPURI BUDAUN','243601','BUDAUN','UTTAR PRADESH','112211222122','ABCDE1211F','SBIN0003555','112211','STATE BANK OF INDIA','BUDAUN','RAMAN','8755881010','BUDAUN','Graduate','NURSERY OWNER',NULL,NULL,'RAMAN','Other','Friend');
INSERT INTO "members" VALUES('M0009','2025-10-28','FAHEEM','RIYASAT','Male','1997-02-01','Single',NULL,'8057092350','GOP PRADHAN WALI GALI, MEERA SARAI BUDAUN','243601','BUDAUN','UTTAR PRADESH','470433736937','AKJPF2462L','SBIN0000623','40840711985','STATE BANK OF INDIA','JOGIPURA BUDAUN','FAIZAN','9528781146','BUDAUN','Secondary','E RICKSHAW',NULL,NULL,'RIYASAT','Parent','Friend');
INSERT INTO "members" VALUES('M0010','2025-10-28','SHAHNVAJ','ARSHAD HUSAIN','Male','1990-01-01','Single',NULL,'6397082076','MAMMAN CHOK KE PASS, CHAKLA NEEM, BUDAUN','243601','BUDAUN','UTTAR PRADESH','656253806646','PALPS2366K','SBIN0005310','34633503219','STATE BANK OF INDIA','JOGIPURA BUDAUN','SURAJ GAFUR','9012183291','KATRA BRAHAMPUR BUDAUN','Illiterate',NULL,NULL,NULL,'SHABANA','Spouse','Friend');
INSERT INTO "members" VALUES('M0011','2025-10-31','ISHTIYAQ','MAULA BAKSH','Male','1997-01-01','Single',NULL,'9557077058','PURANA BAJAR KE PASS BADI SARAI BUDAUN','243601','BUDAUN','UTTAR PRADESH','359197151938','AIVPI4905M','KKBK0000221','7748287816','NEW DELHI KIRTI NAGAR','NEW DELHI','ISLAM','7456970455','KATRA BRAHAMPUR BUDAUN','Illiterate',NULL,NULL,NULL,'MAULA BAKSH','Parent','Friend');
INSERT INTO "members" VALUES('M0012','2025-10-31','MUQTADIR ALI QADRI','SAHID HUSAIN','Male','2002-06-12','Single',NULL,'7830904002','KATRA BRAHAMPUR BUDAUN','243601','BUDAUN','UTTAR PRADESH','862906832090','ABNPQ7049P','SBIN0003555','41139603881','TICKET GANJ BUDAUN','BUDAUN','IRFAN','9536603505','KATRA BRAHAMPUR BUDAUN','Secondary',NULL,NULL,NULL,'SAHID HUSAIN','Parent','Friend');
INSERT INTO "members" VALUES('M0013','2025-10-31','YAWAR HASAN','NAVI HASAN','Male','1997-01-01','Single',NULL,'9027717172','PURANA BAJAR BUDAUN','243601','BUDAUN','UTTAR PRADESH','635846704134','BDJPH1738K','SBIN0008555','43332569196','STATE BANK OF INDIA','BUDAUN CITY TICKET GANJ BUDAUN','SURAJ GAFUR','9012183291','BUDAUN','Secondary','FRUIT VENDOR',NULL,NULL,'NAVI HASAN','Parent','Friend');
INSERT INTO "members" VALUES('M0014','2025-11-01','HABIB','HANEEF','Male','2005-12-05','Single',NULL,'9557228143','MOHALL KHANDHSARI BUDAUN','243601','BUDAUN','UTTAR PRADESH','389110067460','BYBPH3450B','BARB0BADAUN','09838100039382','BANK OF BARODA','BUDAUN','IRFAN',NULL,'BUDAUN','Secondary','VENDOR',NULL,NULL,'HANEEF','Parent','Friend');
CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT,
                loan_id TEXT,
                type TEXT,
                amount REAL,
                pay_date DATE,
                payment_mode TEXT,
                emi_amount REAL,
                advance_amount REAL,
                interest_amount REAL DEFAULT 0,
                FOREIGN KEY (member_id) REFERENCES members (id),
                FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
            );
INSERT INTO "payments" VALUES(1,'M0001','PL0003','loan_disbursed',-20000.0,'2024-12-02','Cash',NULL,NULL,0.0);
INSERT INTO "payments" VALUES(3,'M0002','PL0004','loan_disbursed',-10000.0,'2025-05-21','Cash',NULL,NULL,0.0);
INSERT INTO "payments" VALUES(12,'M0001','PL0001','loan_disbursed',-20000.0,'2024-12-02','NEFT',NULL,NULL,0.0);
INSERT INTO "payments" VALUES(13,'M0001','PL0001','emi',1600.0,'2024-12-15','Cash',1600.0,0.0,1433.33);
INSERT INTO "payments" VALUES(14,'M0001','PL0001','emi',200.0,'2024-01-13','Cash',200.0,0.0,33.33);
INSERT INTO "payments" VALUES(15,'M0001','PL0001','emi',1000.0,'2025-01-21','Cash',1000.0,0.0,833.33);
INSERT INTO "payments" VALUES(16,'M0001','PL0001','emi',2200.0,'2025-02-05','Cash',2200.0,0.0,2033.33);
INSERT INTO "payments" VALUES(17,'M0001','PL0001','emi',3400.0,'2025-02-10','Cash',3400.0,0.0,3233.33);
INSERT INTO "payments" VALUES(18,'M0001','PL0001','emi',1000.0,'2025-02-12','Cash',1000.0,0.0,833.33);
INSERT INTO "payments" VALUES(20,'M0001','PL0001','emi',600.0,'2024-02-15','Cash',600.0,0.0,433.33);
INSERT INTO "payments" VALUES(21,'M0001','PL0001','emi',200.0,'2025-02-28','Cash',200.0,0.0,33.33);
INSERT INTO "payments" VALUES(22,'M0001','PL0001','emi',200.0,'2025-03-01','Cash',200.0,0.0,33.33);
INSERT INTO "payments" VALUES(23,'M0001','PL0001','emi',1000.0,'2025-03-11','Cash',1000.0,0.0,833.33);
INSERT INTO "payments" VALUES(24,'M0001','PL0001','emi',1000.0,'2025-03-17','Cash',1000.0,0.0,833.33);
INSERT INTO "payments" VALUES(25,'M0001','PL0001','emi',1000.0,'2025-03-19','Cash',1000.0,0.0,833.33);
INSERT INTO "payments" VALUES(26,'M0001','PL0001','emi',4000.0,'2025-03-23','Cash',4000.0,0.0,3833.33);
INSERT INTO "payments" VALUES(27,'M0001','PL0001','emi',3400.0,'2025-03-31','Cash',3400.0,0.0,3233.33);
INSERT INTO "payments" VALUES(28,'M0001','PL0001','emi',1600.0,'2025-04-04','Cash',1600.0,0.0,1433.33);
INSERT INTO "payments" VALUES(29,'M0008','PL0002','loan_disbursed',-10000.0,'2024-12-19','Cash',NULL,NULL,0.0);
INSERT INTO "payments" VALUES(30,'M0008','PL0002','emi',300.0,'2024-12-21','Cash',300.0,0.0,216.67);
INSERT INTO "payments" VALUES(31,'M0008','PL0002','emi',200.0,'2024-12-24','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(32,'M0008','PL0002','emi',200.0,'2024-12-26','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(33,'M0008','PL0002','emi',100.0,'2024-12-28','Cash',100.0,0.0,16.67);
INSERT INTO "payments" VALUES(34,'M0008','PL0002','emi',200.0,'2024-12-30','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(35,'M0008','PL0002','emi',100.0,'2025-01-02','Cash',100.0,0.0,16.67);
INSERT INTO "payments" VALUES(36,'M0008','PL0002','emi',100.0,'2025-01-03','Cash',100.0,0.0,16.67);
INSERT INTO "payments" VALUES(37,'M0008','PL0002','emi',300.0,'2025-01-07','Cash',300.0,0.0,216.67);
INSERT INTO "payments" VALUES(38,'M0008','PL0002','emi',600.0,'2025-01-11','Cash',600.0,0.0,516.67);
INSERT INTO "payments" VALUES(39,'M0008','PL0002','emi',200.0,'2025-01-18','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(40,'M0008','PL0002','emi',600.0,'2025-01-21','Cash',600.0,0.0,516.67);
INSERT INTO "payments" VALUES(41,'M0008','PL0002','emi',100.0,'2025-02-05','Cash',100.0,0.0,16.67);
INSERT INTO "payments" VALUES(42,'M0008','PL0002','emi',200.0,'2025-02-08','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(43,'M0008','PL0002','emi',900.0,'2025-02-10','Cash',900.0,0.0,816.67);
INSERT INTO "payments" VALUES(44,'M0008','PL0002','emi',200.0,'2025-02-12','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(45,'M0008','PL0002','emi',200.0,'2025-02-15','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(46,'M0008','PL0002','emi',100.0,'2025-02-18','Cash',100.0,0.0,16.67);
INSERT INTO "payments" VALUES(47,'M0008','PL0002','emi',400.0,'2025-02-22','Cash',400.0,0.0,316.67);
INSERT INTO "payments" VALUES(48,'M0008','PL0002','emi',200.0,'2025-02-27','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(49,'M0008','PL0002','emi',600.0,'2025-02-28','Cash',600.0,0.0,516.67);
INSERT INTO "payments" VALUES(50,'M0008','PL0002','emi',200.0,'2025-03-01','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(51,'M0008','PL0002','emi',600.0,'2025-03-04','Cash',600.0,0.0,516.67);
INSERT INTO "payments" VALUES(52,'M0008','PL0002','emi',200.0,'2025-03-07','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(53,'M0008','PL0002','emi',200.0,'2025-03-08','Cash',200.0,0.0,116.67);
INSERT INTO "payments" VALUES(54,'M0008','PL0002','emi',500.0,'2025-03-26','Cash',500.0,0.0,416.67);
INSERT INTO "payments" VALUES(55,'M0008','PL0002','emi',1500.0,'2025-04-30','Cash',1500.0,0.0,1416.67);
INSERT INTO "payments" VALUES(56,'M0008','PL0002','emi',2000.0,'2025-04-10','Cash',2000.0,0.0,1916.67);
INSERT INTO "payments" VALUES(57,'M0008','PL0002','emi',1000.0,'2025-04-17','Cash',1000.0,0.0,916.67);
CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id TEXT,
                type TEXT,
                amount REAL,
                pay_date DATE,
                payment_mode TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
            );
INSERT INTO "transactions" VALUES(6,'PL0001','emi',1600.0,'2024-12-15','Cash','2025-10-24 18:58:49.708837');
INSERT INTO "transactions" VALUES(7,'PL0001','emi',200.0,'2024-01-13','Cash','2025-10-25 18:55:03.808527');
INSERT INTO "transactions" VALUES(8,'PL0001','emi',1000.0,'2025-01-21','Cash','2025-10-25 18:55:30.476056');
INSERT INTO "transactions" VALUES(9,'PL0001','emi',2200.0,'2025-02-05','Cash','2025-10-25 19:10:08.797822');
INSERT INTO "transactions" VALUES(10,'PL0001','emi',3400.0,'2025-02-10','Cash','2025-10-25 19:10:45.862586');
INSERT INTO "transactions" VALUES(11,'PL0001','emi',1000.0,'2025-02-12','Cash','2025-10-25 19:11:32.078581');
INSERT INTO "transactions" VALUES(13,'PL0001','emi',600.0,'2024-02-15','Cash','2025-10-26 18:05:40.259380');
INSERT INTO "transactions" VALUES(14,'PL0001','emi',200.0,'2025-02-28','Cash','2025-10-26 18:06:07.723427');
INSERT INTO "transactions" VALUES(15,'PL0001','emi',200.0,'2025-03-01','Cash','2025-10-26 18:06:23.176050');
INSERT INTO "transactions" VALUES(16,'PL0001','emi',1000.0,'2025-03-11','Cash','2025-10-26 18:06:48.367671');
INSERT INTO "transactions" VALUES(17,'PL0001','emi',1000.0,'2025-03-17','Cash','2025-10-26 18:07:07.920803');
INSERT INTO "transactions" VALUES(18,'PL0001','emi',1000.0,'2025-03-19','Cash','2025-10-26 18:07:26.504868');
INSERT INTO "transactions" VALUES(19,'PL0001','emi',4000.0,'2025-03-23','Cash','2025-10-26 18:07:43.399988');
INSERT INTO "transactions" VALUES(20,'PL0001','emi',3400.0,'2025-03-31','Cash','2025-10-26 18:08:05.384708');
INSERT INTO "transactions" VALUES(21,'PL0001','emi',1600.0,'2025-04-04','Cash','2025-10-26 18:08:23.079259');
INSERT INTO "transactions" VALUES(22,'PL0002','emi',300.0,'2024-12-21','Cash','2025-10-27 19:06:49.722612');
INSERT INTO "transactions" VALUES(23,'PL0002','emi',200.0,'2024-12-24','Cash','2025-10-27 19:07:19.226096');
INSERT INTO "transactions" VALUES(24,'PL0002','emi',200.0,'2024-12-26','Cash','2025-10-27 19:07:59.705048');
INSERT INTO "transactions" VALUES(25,'PL0002','emi',100.0,'2024-12-28','Cash','2025-10-27 19:08:46.881325');
INSERT INTO "transactions" VALUES(26,'PL0002','emi',200.0,'2024-12-30','Cash','2025-10-27 19:10:29.400057');
INSERT INTO "transactions" VALUES(27,'PL0002','emi',100.0,'2025-01-02','Cash','2025-10-27 19:10:50.406876');
INSERT INTO "transactions" VALUES(28,'PL0002','emi',100.0,'2025-01-03','Cash','2025-10-27 19:11:09.312004');
INSERT INTO "transactions" VALUES(29,'PL0002','emi',300.0,'2025-01-07','Cash','2025-10-27 19:13:26.173592');
INSERT INTO "transactions" VALUES(30,'PL0002','emi',600.0,'2025-01-11','Cash','2025-10-28 19:21:52.335685');
INSERT INTO "transactions" VALUES(31,'PL0002','emi',200.0,'2025-01-18','Cash','2025-10-28 19:22:25.808373');
INSERT INTO "transactions" VALUES(32,'PL0002','emi',600.0,'2025-01-21','Cash','2025-10-28 19:22:49.958727');
INSERT INTO "transactions" VALUES(33,'PL0002','emi',100.0,'2025-02-05','Cash','2025-10-28 19:23:14.125832');
INSERT INTO "transactions" VALUES(34,'PL0002','emi',200.0,'2025-02-08','Cash','2025-10-28 19:23:42.111278');
INSERT INTO "transactions" VALUES(35,'PL0002','emi',900.0,'2025-02-10','Cash','2025-10-28 19:24:01.189063');
INSERT INTO "transactions" VALUES(36,'PL0002','emi',200.0,'2025-02-12','Cash','2025-10-28 19:24:18.655569');
INSERT INTO "transactions" VALUES(37,'PL0002','emi',200.0,'2025-02-15','Cash','2025-10-28 19:24:38.436627');
INSERT INTO "transactions" VALUES(38,'PL0002','emi',100.0,'2025-02-18','Cash','2025-10-28 19:24:59.076492');
INSERT INTO "transactions" VALUES(39,'PL0002','emi',400.0,'2025-02-22','Cash','2025-10-28 19:25:46.414247');
INSERT INTO "transactions" VALUES(40,'PL0002','emi',200.0,'2025-02-27','Cash','2025-10-28 19:26:07.931952');
INSERT INTO "transactions" VALUES(41,'PL0002','emi',600.0,'2025-02-28','Cash','2025-10-28 19:26:37.862976');
INSERT INTO "transactions" VALUES(42,'PL0002','emi',200.0,'2025-03-01','Cash','2025-10-28 19:26:53.518448');
INSERT INTO "transactions" VALUES(43,'PL0002','emi',600.0,'2025-03-04','Cash','2025-10-28 19:27:12.259282');
INSERT INTO "transactions" VALUES(44,'PL0002','emi',200.0,'2025-03-07','Cash','2025-10-28 19:27:30.667067');
INSERT INTO "transactions" VALUES(45,'PL0002','emi',200.0,'2025-03-08','Cash','2025-10-28 19:27:50.220522');
INSERT INTO "transactions" VALUES(46,'PL0002','emi',500.0,'2025-03-26','Cash','2025-10-28 19:28:10.804540');
INSERT INTO "transactions" VALUES(47,'PL0002','emi',1500.0,'2025-04-30','Cash','2025-10-28 19:28:26.579380');
INSERT INTO "transactions" VALUES(48,'PL0002','emi',2000.0,'2025-04-10','Cash','2025-10-28 19:28:44.758283');
INSERT INTO "transactions" VALUES(49,'PL0002','emi',1000.0,'2025-04-17','Cash','2025-10-28 19:29:00.013560');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('investments',3);
INSERT INTO "sqlite_sequence" VALUES('payments',57);
INSERT INTO "sqlite_sequence" VALUES('transactions',49);
INSERT INTO "sqlite_sequence" VALUES('capital_accounts',1);
INSERT INTO "sqlite_sequence" VALUES('fees',2);
INSERT INTO "sqlite_sequence" VALUES('expenses',3);
INSERT INTO "sqlite_sequence" VALUES('deposits',1);
COMMIT;
