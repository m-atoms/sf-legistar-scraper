import sqlite3
import random
from src.scraper.utils import print_legislation_details

def get_random_legislation_file_numbers(db_name='data/legislation.db', num_records=5):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Get all file numbers from the legislation table
    c.execute('''SELECT file_number FROM legislation''')
    all_file_numbers = [row[0] for row in c.fetchall()]
    print(f"total files: {len(all_file_numbers)}")

    conn.close()

    # Generate a list of random file numbers
    random_file_numbers = random.sample(all_file_numbers, min(num_records, len(all_file_numbers)))

    return random_file_numbers

if __name__ == "__main__":
    num_records_to_fetch = 5  # Number of random records to fetch
    random_file_numbers = get_random_legislation_file_numbers(num_records=num_records_to_fetch)

    for file_number in random_file_numbers:
        print_legislation_details(file_number)