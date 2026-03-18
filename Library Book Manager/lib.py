from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import List, Optional

# ---------------- BOOK CLASS ----------------

@dataclass
class Book:
    title: str
    author: str
    isbn: str
    status: str = "available"

    def __post_init__(self):
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.isbn = self.isbn.strip()
        if self.status not in ("available", "issued"):
            self.status = "available"

    def __str__(self):
        return f"{self.title} — {self.author} (ISBN: {self.isbn}) [{self.status}]"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", "").strip(),
            author=data.get("author", "").strip(),
            isbn=data.get("isbn", "").strip(),
            status=data.get("status", "available").strip()
        )

    def is_available(self):
        return self.status == "available"

    def issue(self):
        if self.is_available():
            self.status = "issued"
            return True
        return False

    def return_book(self):
        if not self.is_available():
            self.status = "available"
            return True
        return False


# ---------------- INVENTORY CLASS ----------------

logger = logging.getLogger(__name__)

class LibraryInventory:
    def __init__(self, catalog_path: Path):
        self.catalog_path = Path(catalog_path)
        self.books: List[Book] = []

    def load(self):
        try:
            if not self.catalog_path.exists():
                logger.info("Catalog file not found — creating empty catalog.")
                self.books = []
                return

            with self.catalog_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Catalog JSON root must be a list")

            self.books = [Book.from_dict(entry) for entry in data]
            logger.info(f"Loaded {len(self.books)} books from catalog.")
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            self.books = []

    def save(self):
        try:
            if not self.catalog_path.parent.exists():
                self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

            with self.catalog_path.open("w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.books)} books to catalog.")
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")

    def add_book(self, book: Book):
        if self.search_by_isbn(book.isbn):
            raise ValueError("A book with this ISBN already exists.")
        self.books.append(book)

    def search_by_title(self, title_query: str):
        q = title_query.strip().lower()
        return [b for b in self.books if q in b.title.lower()]

    def search_by_isbn(self, isbn: str):
        s = isbn.strip()
        for b in self.books:
            if b.isbn == s:
                return b
        return None

    def display_all(self):
        return [str(b) for b in self.books]

    def issue_book_by_isbn(self, isbn: str):
        book = self.search_by_isbn(isbn)
        if book is None:
            return False
        return book.issue()

    def return_book_by_isbn(self, isbn: str):
        book = self.search_by_isbn(isbn)
        if book is None:
            return False
        return book.return_book()


# ---------------- CLI ----------------

LOG_FILE = Path("library.log")
CATALOG = Path("catalog.json")

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )

def prompt_non_empty(prompt_text: str):
    while True:
        val = input(prompt_text).strip()
        if val:
            return val
        print("Input cannot be empty.")

def main():
    setup_logging()
    inventory = LibraryInventory(CATALOG)
    inventory.load()

    while True:
        print("\n=== Library Inventory Manager ===")
        print("1. Add Book")
        print("2. Issue Book")
        print("3. Return Book")
        print("4. View All Books")
        print("5. Search")
        print("6. Exit")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            title = prompt_non_empty("Title: ")
            author = prompt_non_empty("Author: ")
            isbn = prompt_non_empty("ISBN: ")
            try:
                inventory.add_book(Book(title, author, isbn))
                inventory.save()
                print("Book added.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            isbn = prompt_non_empty("ISBN to issue: ")
            print("Book issued." if inventory.issue_book_by_isbn(isbn) else "Issue failed.")
            inventory.save()

        elif choice == "3":
            isbn = prompt_non_empty("ISBN to return: ")
            print("Book returned." if inventory.return_book_by_isbn(isbn) else "Return failed.")
            inventory.save()

        elif choice == "4":
            books = inventory.display_all()
            if not books:
                print("No books in catalog.")
            else:
                for b in books:
                    print(b)

        elif choice == "5":
            sub = prompt_non_empty("Search 1) Title  2) ISBN: ")
            if sub == "1":
                q = prompt_non_empty("Title query: ")
                results = inventory.search_by_title(q)
                print("\n".join(str(b) for b in results) if results else "No matches.")
            elif sub == "2":
                q = prompt_non_empty("ISBN: ")
                result = inventory.search_by_isbn(q)
                print(result if result else "No such ISBN.")
            else:
                print("Invalid choice.")

        elif choice == "6":
            print("Exiting.")
            inventory.save()
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
