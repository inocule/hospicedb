# FILENAME 1: db_operations.py

import sqlite3
import os
from contextlib import contextmanager
from constants import TABLE_STRUCTURES

class DatabaseOperations:
    def __init__(self):
        # Create the database directory if it doesn't exist
        os.makedirs('database', exist_ok=True)
        self.db_path = 'database/hospice.db'
        self._setup_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Enable foreign key support
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            conn.close()

    def _setup_database(self):
        # Create database tables if they don't exist"""
        # Drop all tables first in reverse order of dependencies
        drop_tables = [
            'Medical_History',
            'Surgery_History',
            'Patient_Profile',
            'Credential',
            'Disease_Masterlist'
        ]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for table in drop_tables:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
            conn.commit()
        
        # Create database tables
        tables = {
            'Disease_Masterlist': '''
                CREATE TABLE IF NOT EXISTS Disease_Masterlist (
                    diseaseName VARCHAR(50) NOT NULL,
                    illnessCode CHAR(3) PRIMARY KEY
                )
            ''',
            'Credential': '''
                CREATE TABLE IF NOT EXISTS Credential (
                    patientNumber VARCHAR(5) PRIMARY KEY,
                    patientName VARCHAR(100) NOT NULL,
                    birthdate DATE,
                    civilStatus CHAR(2) DEFAULT 'S',
                    occupation VARCHAR(20),
                    religion VARCHAR(30),
                    education CHAR(2) DEFAULT 'N',
                    illnessCode TEXT,
                    diseaseName TEXT,
                    detectionDate TEXT,
                    medicinesTaken TEXT,
                    surgeryHistory TEXT,
                    surgeryDate TEXT,
                    contact VARCHAR(30),
                    emergencyPhone VARCHAR(14),
                    relationship VARCHAR(30)
                )
            ''',
            'Patient_Profile': '''
                CREATE TABLE IF NOT EXISTS Patient_Profile (
                    patientNumber VARCHAR(5) PRIMARY KEY,
                    patientName VARCHAR(100) NOT NULL,
                    birthdate DATE,
                    civilStatus CHAR(2) DEFAULT 'S',
                    occupation VARCHAR(20),
                    religion VARCHAR(30),
                    education CHAR(2) DEFAULT 'N',
                    contact VARCHAR(30),
                    emergencyPhone VARCHAR(14),
                    relationship VARCHAR(30),
                    FOREIGN KEY (patientNumber) REFERENCES Credential(patientNumber) ON DELETE CASCADE
                )
            ''',
            'Medical_History': '''
                CREATE TABLE IF NOT EXISTS Medical_History (
                    patientNumber VARCHAR(5),
                    illnessCode CHAR(3),
                    detectionDate DATE,
                    medicinesTaken VARCHAR(20),
                    PRIMARY KEY (patientNumber, illnessCode),
                    FOREIGN KEY (patientNumber) REFERENCES Credential(patientNumber) ON DELETE CASCADE,
                    FOREIGN KEY (illnessCode) REFERENCES Disease_Masterlist(illnessCode)
                )
            ''',
            'Surgery_History': '''
                CREATE TABLE IF NOT EXISTS Surgery_History (
                    surgeryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    patientNumber VARCHAR(5),
                    surgeryHistory VARCHAR(30),
                    surgeryDate DATE,
                    FOREIGN KEY (patientNumber) REFERENCES Credential(patientNumber) ON DELETE CASCADE
                )
            '''
        }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for query in tables.values():
                cursor.execute(query)
            
            # Insert initial patient data
            initial_data = [
                {
                    'patientNumber': '1',
                    'patientName': 'Carl Jayvin Lee',
                    'birthDate': '2004-08-16',
                    'civilStatus': 'S',
                    'occupation': 'Student',
                    'religion': 'Buddhism',
                    'education': 'P',
                    'illnessCode': 'TB, SH, BD',
                    'diseaseName': 'Tuberculosis, Shingles, Brain Damage',
                    'detectionDate': '2012-12-02, 2018-04-27, 2022-09-02',
                    'medicinesTaken': 'Rifampin, Acyclovir, Aspirin',
                    'surgeryHistory': 'Laparoscopic, Spinal Fusion, N/A',
                    'surgeryDate': '2022-02-22, 2022-02-23, N/A',
                    'contact': 'Chrysler Lee',
                    'emergencyPhone': '+234912345678',
                    'relationship': 'Brother'
                },
                {
                    'patientNumber': '2',
                    'patientName': 'Vinjireh Caasi',
                    'birthDate': '2005-09-06',
                    'civilStatus': 'S',
                    'occupation': 'Student',
                    'religion': 'Christianity',
                    'education': 'J',
                    'illnessCode': 'CC, GNR',
                    'diseaseName': 'Cancer, Gonorrhea',
                    'detectionDate': '2010-08-16, 2012-09-06',
                    'medicinesTaken': 'Niacinamide, Salycilic Acid',
                    'surgeryHistory': 'N/A, N/A',
                    'surgeryDate': 'N/A, N/A',
                    'contact': 'Anna Lynn Caasi',
                    'emergencyPhone': '+639150533867',
                    'relationship': 'Mother'
                },
                {
                    'patientNumber': '3',
                    'patientName': 'Bouie Martinez',
                    'birthDate': '2005-02-10',
                    'civilStatus': 'S',
                    'occupation': 'Student',
                    'religion': 'Muslim',
                    'education': 'S',
                    'illnessCode': 'BD, DI',
                    'diseaseName': 'Brain Damage, Diabetes',
                    'detectionDate': '2022-03-12, 2024-08-13',
                    'medicinesTaken': 'Aspirin, Insulin',
                    'surgeryHistory': 'Toe Amputation, N/A',
                    'surgeryDate': '2025-03-25, N/A',
                    'contact': 'Abegail Martinez',
                    'emergencyPhone': '+639219733059',
                    'relationship': 'Mother'
                },
                {
                    'patientNumber': '4',
                    'patientName': 'Hans Naperi',
                    'birthDate': '2005-07-28',
                    'civilStatus': 'M',
                    'occupation': 'Student',
                    'religion': "Jehovah's Witness",
                    'education': 'U',
                    'illnessCode': 'PN, AS, FL, BR',
                    'diseaseName': 'Pneumonia, Asthma, Flu, Bronchitis',
                    'detectionDate': '2021-12-25, 2022-08-06, 2023-11-15, 2025-01-03',
                    'medicinesTaken': 'Medicol, Ascorbic Acid, Salbutamol, Paracetamol',
                    'surgeryHistory': 'N/A, N/A, Tonsillectomy, N/A',
                    'surgeryDate': 'N/A, N/A, 2023-10-10, N/A',
                    'contact': 'Mary Ann Naperi',
                    'emergencyPhone': '+639157909485',
                    'relationship': 'Mother'
                }
            ]

            # Insert data into tables
            for data in initial_data:
                # First insert into Credential
                cred_columns = ", ".join(TABLE_STRUCTURES["Credential"])
                cred_placeholders = ", ".join(["?" for _ in TABLE_STRUCTURES["Credential"]])
                cred_values = [data[col] for col in TABLE_STRUCTURES["Credential"]]
                
                cursor.execute(f'''
                    INSERT INTO Credential ({cred_columns})
                    VALUES ({cred_placeholders})
                ''', cred_values)

                # Then insert into Patient_Profile
                profile_columns = ", ".join(TABLE_STRUCTURES["Patient_Profile"])
                profile_placeholders = ", ".join(["?" for _ in TABLE_STRUCTURES["Patient_Profile"]])
                profile_values = [data[col] for col in TABLE_STRUCTURES["Patient_Profile"]]
                
                cursor.execute(f'''
                    INSERT INTO Patient_Profile ({profile_columns})
                    VALUES ({profile_placeholders})
                ''', profile_values)

                # Normalize and insert medical history
                normalized_data = self.normalize_multi_values(data)

                # Insert disease masterlist and medical history records
                for record in normalized_data['illnessCode']:
                    if record['illnessCode'] != 'N/A':
                        # Insert into Disease_Masterlist if not exists
                        cursor.execute('''
                            INSERT OR IGNORE INTO Disease_Masterlist (diseaseName, illnessCode)
                            VALUES (?, ?)
                        ''', (record['diseaseName'], record['illnessCode']))

                        # Insert medical history
                        cursor.execute('''
                            INSERT INTO Medical_History 
                            (patientNumber, illnessCode, detectionDate, medicinesTaken)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            data['patientNumber'],
                            record['illnessCode'],
                            record['detectionDate'],
                            record['medicinesTaken']
                        ))

                # Insert surgery history records
                for record in normalized_data['surgeryHistory']:
                    if record['surgeryHistory'] != 'N/A':
                        cursor.execute('''
                            INSERT INTO Surgery_History 
                            (patientNumber, surgeryHistory, surgeryDate)
                            VALUES (?, ?, ?)
                        ''', (
                            data['patientNumber'],
                            record['surgeryHistory'],
                            record['surgeryDate']
                        ))

            conn.commit()

    def normalize_multi_values(self, data):
        """Normalize multi-valued fields into separate records"""
        multi_valued_fields = {
            'illnessCode': ['illnessCode', 'diseaseName', 'detectionDate', 'medicinesTaken'],
            'surgeryHistory': ['surgeryHistory', 'surgeryDate']
        }

        normalized_data = {}
        for key_field, fields in multi_valued_fields.items():
            if key_field in data and data[key_field]:
                # Split values and clean them
                values = {}
                for field in fields:
                    if field in data and data[field]:
                        values[field] = [v.strip() for v in data[field].split(',')]
                    else:
                        values[field] = []

                # Get the maximum length
                max_len = max(len(v) for v in values.values()) if values else 0

                # Normalize to same length with N/A
                records = []
                for i in range(max_len):
                    record = {}
                    for field in fields:
                        field_values = values.get(field, [])
                        record[field] = field_values[i] if i < len(field_values) else 'N/A'
                    records.append(record)

                normalized_data[key_field] = records
            else:
                normalized_data[key_field] = []

        return normalized_data

    def insert_normalized_data(self, credential_data, patient_profile_data, medical_data, surgery_data):
        """Insert data into normalized tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # First insert into Credential (1NF)
                cred_columns = ", ".join(TABLE_STRUCTURES["Credential"])
                cred_placeholders = ", ".join(["?" for _ in TABLE_STRUCTURES["Credential"]])
                cred_values = [credential_data[col] for col in TABLE_STRUCTURES["Credential"]]
                
                cursor.execute(f'''
                    INSERT INTO Credential ({cred_columns})
                    VALUES ({cred_placeholders})
                ''', cred_values)

                # Then insert Patient Profile data
                profile_columns = ", ".join(TABLE_STRUCTURES["Patient_Profile"])
                profile_placeholders = ", ".join(["?" for _ in TABLE_STRUCTURES["Patient_Profile"]])
                profile_values = [patient_profile_data[col] for col in TABLE_STRUCTURES["Patient_Profile"]]
                
                cursor.execute(f'''
                    INSERT INTO Patient_Profile ({profile_columns})
                    VALUES ({profile_placeholders})
                ''', profile_values)

                # Normalize multi-valued data
                normalized_data = self.normalize_multi_values(credential_data)

                # Insert Medical History records
                for record in normalized_data['illnessCode']:
                    if record['illnessCode'] != 'N/A':
                        # First check if disease exists in masterlist
                        cursor.execute(
                            "SELECT illnessCode FROM Disease_Masterlist WHERE illnessCode = ?", 
                            (record['illnessCode'],)
                        )
                        if not cursor.fetchone():
                            cursor.execute('''
                                INSERT INTO Disease_Masterlist (diseaseName, illnessCode)
                                VALUES (?, ?)
                            ''', (record['diseaseName'], record['illnessCode']))

                        # Then insert medical history
                        cursor.execute('''
                            INSERT INTO Medical_History 
                            (patientNumber, illnessCode, detectionDate, medicinesTaken)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            patient_profile_data['patientNumber'],
                            record['illnessCode'],
                            record['detectionDate'],
                            record['medicinesTaken']
                        ))

                # Insert Surgery History records
                for record in normalized_data['surgeryHistory']:
                    if record['surgeryHistory'] != 'N/A':
                        cursor.execute('''
                            INSERT INTO Surgery_History 
                            (patientNumber, surgeryHistory, surgeryDate)
                            VALUES (?, ?, ?)
                        ''', (
                            patient_profile_data['patientNumber'],
                            record['surgeryHistory'],
                            record['surgeryDate']
                        ))

                conn.commit()
                return True
            except sqlite3.Error as e:
                conn.rollback()
                raise e

    def fetch_data(self, table_name):
        """Generic fetch data method"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if table_name == "Credential":
                # Get columns in the correct order from TABLE_STRUCTURES
                columns = ", ".join(TABLE_STRUCTURES[table_name])
                cursor.execute(f'SELECT {columns} FROM {table_name}')
            else:
                # For normalized tables, get their specific columns
                columns = ", ".join(TABLE_STRUCTURES[table_name])
                cursor.execute(f'SELECT {columns} FROM {table_name}')
            
            return cursor.fetchall()

    def execute_custom_query(self, query):
        """Execute a custom SQL query"""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                self.cursor = cursor  # Store cursor for column names
                
                # For SELECT queries, return the results
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                # For other queries (INSERT, UPDATE, DELETE), commit and return affected rows
                else:
                    conn.commit()
                    return [(f"{cursor.rowcount} rows affected",)]
            except sqlite3.Error as e:
                conn.rollback()
                raise e

    def insert_disease_masterlist(self, data):
        """Insert disease masterlist data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Disease_Masterlist (diseaseName, illnessCode) VALUES (?, ?)',
                (data['diseaseName'], data['illnessCode'])
            )
            conn.commit()
            return True

    def get_current_values(self, patient_number, illness_code):
        """Get current values for a record using patient number and illness code"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # First get the Credential record
                cursor.execute("""
                    SELECT c.patientNumber, c.patientName, c.birthDate, c.civilStatus,
                           c.occupation, c.religion, c.education, c.illnessCode,
                           c.diseaseName, c.detectionDate, c.medicinesTaken,
                           c.surgeryHistory, c.surgeryDate, c.contact,
                           c.emergencyPhone, c.relationship
                    FROM Credential c
                    WHERE c.patientNumber = ?
                """, (patient_number,))
                credential_row = cursor.fetchone()
                
                if not credential_row:
                    return None
                
                # Convert to dictionary using column names from TABLE_STRUCTURES
                credential_data = {}
                columns = TABLE_STRUCTURES["Credential"]
                for idx, col in enumerate(columns):
                    credential_data[col] = credential_row[idx] if idx < len(credential_row) else None
                
                # Get the specific Medical_History record
                cursor.execute("""
                    SELECT * FROM Medical_History 
                    WHERE patientNumber = ? AND illnessCode = ?
                """, (patient_number, illness_code))
                medical_row = cursor.fetchone()
                
                if medical_row:
                    # Add medical history data
                    for idx, col in enumerate(cursor.description):
                        credential_data[col[0]] = medical_row[idx]
                
                # Get the Surgery_History records
                cursor.execute("""
                    SELECT * FROM Surgery_History 
                    WHERE patientNumber = ?
                """, (patient_number,))
                surgery_rows = cursor.fetchall()
                
                if surgery_rows:
                    # Combine surgery history data
                    surgery_histories = []
                    surgery_dates = []
                    for row in surgery_rows:
                        surgery_histories.append(row[2])  # surgeryHistory
                        surgery_dates.append(row[3])      # surgeryDate
                    
                    credential_data['surgeryHistory'] = ', '.join(surgery_histories)
                    credential_data['surgeryDate'] = ', '.join(surgery_dates)
                
                return credential_data
                
            except sqlite3.Error as e:
                conn.rollback()
                raise e

    def update_data(self, table_name, data, conditions):
        """Update data in specified table"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                if table_name == "Credential":
                    # Update Credential first
                    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                    values = list(data.values()) + [conditions["patientNumber"]]
                    
                    cursor.execute(f'''
                        UPDATE Credential 
                        SET {set_clause}
                        WHERE patientNumber = ?
                    ''', values)

                    # Update Patient_Profile
                    profile_data = {k: data[k] for k in TABLE_STRUCTURES["Patient_Profile"]}
                    profile_set = ", ".join([f"{k} = ?" for k in profile_data.keys()])
                    profile_values = list(profile_data.values()) + [conditions["patientNumber"]]
                    
                    cursor.execute(f'''
                        UPDATE Patient_Profile 
                        SET {profile_set}
                        WHERE patientNumber = ?
                    ''', profile_values)

                    # Delete existing medical and surgery records
                    cursor.execute("DELETE FROM Medical_History WHERE patientNumber = ? AND illnessCode = ?", 
                                (conditions["patientNumber"], conditions["illnessCode"]))
                    cursor.execute("DELETE FROM Surgery_History WHERE patientNumber = ?", 
                                (conditions["patientNumber"],))

                    # Insert new records using normalize_multi_values
                    normalized_data = self.normalize_multi_values(data)

                    # Insert Medical History records
                    for record in normalized_data['illnessCode']:
                        if record['illnessCode'] != 'N/A':
                            # Check if disease exists in masterlist
                            cursor.execute(
                                "SELECT illnessCode FROM Disease_Masterlist WHERE illnessCode = ?", 
                                (record['illnessCode'],)
                            )
                            if not cursor.fetchone():
                                cursor.execute('''
                                    INSERT INTO Disease_Masterlist (diseaseName, illnessCode)
                                    VALUES (?, ?)
                                ''', (record['diseaseName'], record['illnessCode']))

                            # Insert medical history
                            cursor.execute('''
                                INSERT INTO Medical_History 
                                (patientNumber, illnessCode, detectionDate, medicinesTaken)
                                VALUES (?, ?, ?, ?)
                            ''', (
                                conditions["patientNumber"],
                                record['illnessCode'],
                                record['detectionDate'],
                                record['medicinesTaken']
                            ))

                    # Insert Surgery History records
                    for record in normalized_data['surgeryHistory']:
                        if record['surgeryHistory'] != 'N/A':
                            cursor.execute('''
                                INSERT INTO Surgery_History 
                                (patientNumber, surgeryHistory, surgeryDate)
                                VALUES (?, ?, ?)
                            ''', (
                                conditions["patientNumber"],
                                record['surgeryHistory'],
                                record['surgeryDate']
                            ))
                else:
                    # For other tables, do a simple update
                    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                    where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
                    values = list(data.values()) + list(conditions.values())
                    
                    cursor.execute(f'''
                        UPDATE {table_name}
                        SET {set_clause}
                        WHERE {where_clause}
                    ''', values)

                conn.commit()
                return True
            except sqlite3.Error as e:
                conn.rollback()
                raise e

    def batch_delete_records(self, table_name, records):
        """Delete multiple records"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Delete from Credential - will cascade to other tables
                placeholders = ",".join("?" * len(records))
                cursor.execute(f'''
                    DELETE FROM Credential
                    WHERE patientNumber IN ({placeholders})
                ''', records)
                
                conn.commit()
                return True
            except sqlite3.Error as e:
                conn.rollback()
                raise e

    def delete_from_disease_masterlist(self, illness_codes):
        """Delete records from Disease_Masterlist by illness codes"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # First check if any illness codes are referenced in Medical_History
                placeholders = ','.join(['?' for _ in illness_codes])
                cursor.execute(f"""
                    SELECT DISTINCT illnessCode 
                    FROM Medical_History 
                    WHERE illnessCode IN ({placeholders})
                """, illness_codes)
                
                referenced_codes = [row[0] for row in cursor.fetchall()]
                
                if referenced_codes:
                    # Some illness codes are still referenced
                    codes_str = ', '.join(referenced_codes)
                    raise sqlite3.IntegrityError(
                        f"Cannot delete illness codes: {codes_str}. "
                        "They are still referenced in Medical History records."
                    )
                
                # If we get here, none of the codes are referenced, safe to delete
                cursor.execute(f"""
                    DELETE FROM Disease_Masterlist 
                    WHERE illnessCode IN ({placeholders})
                """, illness_codes)
                
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                conn.rollback()
                raise e