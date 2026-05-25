"""
Dataset Generator for Library Management System - Phase 2
Generates synthetic CSV files with 150+ records for ETL pipeline.

Run from backend/ directory:
    python -c "from etl.generate_dataset import generate_all; generate_all()"
"""

import csv
import os
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# ─────────────────────────────────────────────────────────────
# MASTER BOOK LIST  (50 books, 8 categories)
# ─────────────────────────────────────────────────────────────
BOOKS = [
    # Fiction (10)
    (1,  "The Great Gatsby",                           "F. Scott Fitzgerald",  "Fiction",     "978-0-7432-7356-5"),
    (2,  "To Kill a Mockingbird",                      "Harper Lee",           "Fiction",     "978-0-06-112008-4"),
    (3,  "1984",                                        "George Orwell",        "Fiction",     "978-0-45-228285-3"),
    (4,  "Pride and Prejudice",                        "Jane Austen",          "Fiction",     "978-0-14-143951-8"),
    (5,  "The Alchemist",                              "Paulo Coelho",         "Fiction",     "978-0-06-231500-7"),
    (6,  "Brave New World",                            "Aldous Huxley",        "Fiction",     "978-0-06-085052-4"),
    (7,  "Of Mice and Men",                            "John Steinbeck",       "Fiction",     "978-0-14-028726-3"),
    (8,  "The Catcher in the Rye",                    "J.D. Salinger",        "Fiction",     "978-0-31-676948-0"),
    (9,  "The Road",                                   "Cormac McCarthy",      "Fiction",     "978-0-30-726543-1"),
    (10, "Beloved",                                    "Toni Morrison",        "Fiction",     "978-1-40-031218-7"),
    # Technology (10)
    (11, "Clean Code",                                 "Robert C. Martin",     "Technology",  "978-0-13-235088-4"),
    (12, "The Pragmatic Programmer",                   "Andrew Hunt",          "Technology",  "978-0-20-161622-4"),
    (13, "Design Patterns",                            "Gang of Four",         "Technology",  "978-0-20-163361-0"),
    (14, "Introduction to Algorithms",                 "Thomas H. Cormen",     "Technology",  "978-0-26-203293-3"),
    (15, "The Art of Computer Programming",            "Donald Knuth",         "Technology",  "978-0-20-175104-0"),
    (16, "Structure and Interpretation of Computer Programs", "Harold Abelson","Technology",  "978-0-26-251087-5"),
    (17, "Code Complete",                              "Steve McConnell",      "Technology",  "978-0-73-561967-8"),
    (18, "Refactoring",                                "Martin Fowler",        "Technology",  "978-0-20-148567-7"),
    (19, "The Mythical Man-Month",                     "Frederick Brooks",     "Technology",  "978-0-20-183595-3"),
    (20, "You Dont Know JS",                           "Kyle Simpson",         "Technology",  "978-1-49-194041-5"),
    # Science (8)
    (21, "A Brief History of Time",                    "Stephen Hawking",      "Science",     "978-0-55-338016-3"),
    (22, "The Selfish Gene",                           "Richard Dawkins",      "Science",     "978-0-19-286092-7"),
    (23, "Cosmos",                                     "Carl Sagan",           "Science",     "978-0-34-539338-1"),
    (24, "The Origin of Species",                      "Charles Darwin",       "Science",     "978-0-14-043205-3"),
    (25, "Thinking Fast and Slow",                     "Daniel Kahneman",      "Science",     "978-0-37-427563-1"),
    (26, "The Double Helix",                           "James Watson",         "Science",     "978-0-74-322629-2"),
    (27, "Sapiens",                                    "Yuval Noah Harari",    "Science",     "978-0-06-231609-7"),
    (28, "Homo Deus",                                  "Yuval Noah Harari",    "Science",     "978-0-06-246431-6"),
    # History (5)
    (29, "Guns Germs and Steel",                       "Jared Diamond",        "History",     "978-0-39-331755-8"),
    (30, "The Rise and Fall of the Third Reich",       "William Shirer",       "History",     "978-0-67-172868-7"),
    (31, "A Peoples History of the United States",     "Howard Zinn",          "History",     "978-0-06-083792-7"),
    (32, "The Silk Roads",                             "Peter Frankopan",      "History",     "978-1-10-190422-1"),
    (33, "SPQR",                                       "Mary Beard",           "History",     "978-1-46-795982-4"),
    # Biography (5)
    (34, "Steve Jobs",                                 "Walter Isaacson",      "Biography",   "978-1-45-161797-8"),
    (35, "The Diary of a Young Girl",                  "Anne Frank",           "Biography",   "978-0-55-315489-5"),
    (36, "Long Walk to Freedom",                       "Nelson Mandela",       "Biography",   "978-0-31-610771-7"),
    (37, "Einstein His Life and Universe",             "Walter Isaacson",      "Biography",   "978-0-74-327381-0"),
    (38, "Leonardo da Vinci",                          "Walter Isaacson",      "Biography",   "978-1-50-114289-8"),
    # Self-Help (5)
    (39, "Atomic Habits",                              "James Clear",          "Self-Help",   "978-0-73-521129-2"),
    (40, "The 7 Habits of Highly Effective People",    "Stephen Covey",        "Self-Help",   "978-1-45-162901-8"),
    (41, "How to Win Friends and Influence People",    "Dale Carnegie",        "Self-Help",   "978-0-67-142517-6"),
    (42, "Mans Search for Meaning",                    "Viktor Frankl",        "Self-Help",   "978-0-80-706996-7"),
    (43, "Deep Work",                                  "Cal Newport",          "Self-Help",   "978-1-45-554128-8"),
    # Mystery (5)
    (44, "The Girl with the Dragon Tattoo",            "Stieg Larsson",        "Mystery",     "978-0-30-726975-4"),
    (45, "Gone Girl",                                  "Gillian Flynn",        "Mystery",     "978-0-30-758836-4"),
    (46, "The Da Vinci Code",                          "Dan Brown",            "Mystery",     "978-0-38-550420-5"),
    (47, "Murder on the Orient Express",               "Agatha Christie",      "Mystery",     "978-0-06-207350-5"),
    (48, "The Name of the Rose",                       "Umberto Eco",          "Mystery",     "978-0-15-144647-6"),
    # Non-Fiction (2)
    (49, "Outliers",                                   "Malcolm Gladwell",     "Non-Fiction", "978-0-31-617138-7"),
    (50, "The Tipping Point",                          "Malcolm Gladwell",     "Non-Fiction", "978-0-31-634632-7"),
]

# ─────────────────────────────────────────────────────────────
# BORROWERS  (30 members)
# ─────────────────────────────────────────────────────────────
BORROWERS = [
    (1,  "Alice Johnson",    "alice.johnson@email.com",    "555-0101"),
    (2,  "Bob Smith",        "bob.smith@email.com",        "555-0102"),
    (3,  "Carol Williams",   "carol.williams@email.com",   "555-0103"),
    (4,  "David Brown",      "david.brown@email.com",      "555-0104"),
    (5,  "Emma Davis",       "emma.davis@email.com",       "555-0105"),
    (6,  "Frank Miller",     "frank.miller@email.com",     "555-0106"),
    (7,  "Grace Wilson",     "grace.wilson@email.com",     "555-0107"),
    (8,  "Henry Moore",      "henry.moore@email.com",      "555-0108"),
    (9,  "Isabella Taylor",  "isabella.taylor@email.com",  "555-0109"),
    (10, "James Anderson",   "james.anderson@email.com",   "555-0110"),
    (11, "Katherine Thomas", "katherine.thomas@email.com", "555-0111"),
    (12, "Liam Jackson",     "liam.jackson@email.com",     "555-0112"),
    (13, "Mia White",        "mia.white@email.com",        "555-0113"),
    (14, "Noah Harris",      "noah.harris@email.com",      "555-0114"),
    (15, "Olivia Martin",    "olivia.martin@email.com",    "555-0115"),
    (16, "Patrick Thompson", "patrick.thompson@email.com", "555-0116"),
    (17, "Quinn Garcia",     "quinn.garcia@email.com",     "555-0117"),
    (18, "Rachel Martinez",  "rachel.martinez@email.com",  "555-0118"),
    (19, "Samuel Robinson",  "samuel.robinson@email.com",  "555-0119"),
    (20, "Tara Clark",       "tara.clark@email.com",       "555-0120"),
    (21, "Uma Rodriguez",    "uma.rodriguez@email.com",    "555-0121"),
    (22, "Victor Lewis",     "victor.lewis@email.com",     "555-0122"),
    (23, "Wendy Lee",        "wendy.lee@email.com",        "555-0123"),
    (24, "Xavier Walker",    "xavier.walker@email.com",    "555-0124"),
    (25, "Yara Hall",        "yara.hall@email.com",        "555-0125"),
    (26, "Zachary Allen",    "zachary.allen@email.com",    "555-0126"),
    (27, "Amy Young",        "amy.young@email.com",        "555-0127"),
    (28, "Brian King",       "brian.king@email.com",       "555-0128"),
    (29, "Cynthia Wright",   "cynthia.wright@email.com",   "555-0129"),
    (30, "Daniel Scott",     "daniel.scott@email.com",     "555-0130"),
]

# ─────────────────────────────────────────────────────────────
# TRANSACTION GENERATOR
# ─────────────────────────────────────────────────────────────
def generate_transactions(today=None):
    """
    Generate 180+ realistic transactions:
      - 110 returned  (have return_date)
      -  40 overdue   (no return_date, borrow_date > 14 days ago)
      -  30+ active   (no return_date, borrow_date <= 14 days ago)
    """
    random.seed(42)
    if today is None:
        today = datetime(2026, 5, 25)

    transactions = []
    tid = 1
    active_books: set = set()   # tracks books currently borrowed

    # ── 110 returned transactions ──────────────────────────
    for _ in range(110):
        book_id = random.randint(1, 50)
        borrower_id = random.randint(1, 30)
        days_ago = random.randint(30, 730)
        borrow_date = today - timedelta(days=days_ago)
        duration = random.randint(3, 25)
        return_date = borrow_date + timedelta(days=duration)
        if return_date >= today:
            return_date = today - timedelta(days=1)
        transactions.append((
            tid, book_id, borrower_id,
            borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            return_date.strftime('%Y-%m-%d %H:%M:%S'),
        ))
        tid += 1

    # ── 40 overdue transactions ────────────────────────────
    for _ in range(60):                  # try 60 times to find 40 unique books
        if len([t for t in transactions if not t[4]]) >= 40:
            break
        book_id = random.randint(1, 50)
        if book_id in active_books:
            continue
        borrower_id = random.randint(1, 30)
        days_ago = random.randint(15, 90)
        borrow_date = today - timedelta(days=days_ago)
        active_books.add(book_id)
        transactions.append((
            tid, book_id, borrower_id,
            borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            '',    # no return → overdue
        ))
        tid += 1

    # ── 30 active-not-overdue transactions ─────────────────
    for _ in range(50):
        if len([t for t in transactions if not t[4]]) >= 70:
            break
        book_id = random.randint(1, 50)
        if book_id in active_books:
            continue
        borrower_id = random.randint(1, 30)
        days_ago = random.randint(1, 13)
        borrow_date = today - timedelta(days=days_ago)
        active_books.add(book_id)
        transactions.append((
            tid, book_id, borrower_id,
            borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            '',    # no return → active
        ))
        tid += 1

    return transactions


# ─────────────────────────────────────────────────────────────
# CSV WRITERS
# ─────────────────────────────────────────────────────────────
def write_books_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, 'books.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['book_id', 'title', 'author', 'category', 'isbn', 'availability_status'])
        for b in BOOKS:
            w.writerow([*b, 'available'])
    print(f"  ✔ books.csv        ({len(BOOKS)} records)")
    return path


def write_borrowers_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, 'borrowers.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['borrower_id', 'borrower_name', 'email', 'phone'])
        for b in BORROWERS:
            w.writerow(b)
    print(f"  ✔ borrowers.csv    ({len(BORROWERS)} records)")
    return path


def write_transactions_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    txns = generate_transactions()
    path = os.path.join(DATA_DIR, 'transactions.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['transaction_id', 'book_id', 'borrower_id', 'borrow_date', 'return_date'])
        for t in txns:
            w.writerow(t)
    print(f"  ✔ transactions.csv ({len(txns)} records)")
    return path


def generate_all(force=False):
    """Generate all CSV dataset files."""
    os.makedirs(DATA_DIR, exist_ok=True)
    files = ['books.csv', 'borrowers.csv', 'transactions.csv']
    all_exist = all(os.path.exists(os.path.join(DATA_DIR, f)) for f in files)

    if all_exist and not force:
        print("  Dataset files already exist (use force=True to regenerate).")
        return

    print("Generating dataset files…")
    write_books_csv()
    write_borrowers_csv()
    write_transactions_csv()
    print("Dataset generation complete.\n")


if __name__ == '__main__':
    generate_all(force=True)
