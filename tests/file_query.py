import sqlite3
import sys
from src.scraper.utils import print_legislation_details

def get_legislation_details(file_number, db_name='data/legislation.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Check if the file number exists in the database
    c.execute('''SELECT COUNT(*) FROM legislation WHERE file_number = ?''', (file_number,))
    count = c.fetchone()[0]

    conn.close()

    if count == 0:
        print(f"Error: File number {file_number} not found in the database.")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_number>")
        sys.exit(1)

    file_number = sys.argv[1]
    
    if get_legislation_details(file_number):
        print_legislation_details(file_number)