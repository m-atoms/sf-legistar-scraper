import sqlite3

def connect_db():
    return sqlite3.connect('data/legislation.db')

def create_tables():
    conn = connect_db()
    c = conn.cursor()

    # Create legislation table with an auto-incrementing id
    c.execute('''CREATE TABLE IF NOT EXISTS legislation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, file_number TEXT, type TEXT, introduced TEXT, 
                  on_agenda TEXT, enactment_date TEXT, name TEXT, status TEXT, in_control TEXT, 
                  final_action TEXT, enactment_number TEXT, title TEXT, sponsors TEXT, url TEXT)''')

    # Create history table with a foreign key to legislation
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, legislation_id INTEGER, date TEXT, ver TEXT, 
                  action_by TEXT, action TEXT, result TEXT, 
                  FOREIGN KEY(legislation_id) REFERENCES legislation(id))''')

    conn.commit()
    conn.close()

def store_in_database(data):
    conn = connect_db()
    c = conn.cursor()

    # Insert data into legislation table
    c.execute('''INSERT INTO legislation (file_number, type, introduced, on_agenda, enactment_date, 
                                          name, status, in_control, final_action, enactment_number, 
                                          title, sponsors, url) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (data['file_number'], data['type'], data['introduced'], data['on_agenda'], data['enactment_date'],
                  data['name'], data['status'], data['in_control'], data['final_action'], data['enactment_number'],
                  data['title'], data['sponsors'], data['url']))

    # Get the id of the newly inserted legislation record
    legislation_id = c.lastrowid

    # Insert history data into history table
    for record in data['history']:
        c.execute('''INSERT INTO history (legislation_id, date, ver, action_by, action, result) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                     (legislation_id, record['date'], record['ver'], record['action_by'], record['action'], record['result']))

    conn.commit()
    conn.close()
