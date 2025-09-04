import csv
import json
from app import create_app, db
from app.models import Book

app = create_app()


def import_books():
    with app.app_context():
        # Очищаем существующие книги
        Book.query.delete()

        # Импорт из CSV
        try:
            with open('book_catalog_sample.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, 1):
                    try:
                        book = Book(
                            title=row['title'],
                            author=row['author'],
                            price=float(row['price']),
                            genre=row['genre'],
                            cover_url=row['cover_url'],
                            description=row['description'],
                            rating=float(row['rating']),
                            year=int(row['year'])
                        )
                        db.session.add(book)
                        print(f"Добавлена книга {i}: {row['title']}")
                    except (ValueError, KeyError) as e:
                        print(f"Ошибка в строке {i}: {e}")
        except FileNotFoundError:
            print("CSV файл не найден")

        # Импорт из JSON
        try:
            with open('books_catalog.json', 'r', encoding='utf-8') as jsonfile:
                books_data = json.load(jsonfile)
                for i, book_data in enumerate(books_data, 1):
                    try:
                        book = Book(
                            title=book_data['title'],
                            author=book_data['author'],
                            price=float(book_data['price']),
                            genre=book_data['genre'],
                            cover_url=book_data['cover'],
                            description=book_data['description'],
                            rating=float(book_data['rating']),
                            year=int(book_data['year'])
                        )
                        db.session.add(book)
                        print(f"Добавлена книга из JSON {i}: {book_data['title']}")
                    except (ValueError, KeyError) as e:
                        print(f"Ошибка в JSON объекте {i}: {e}")
        except FileNotFoundError:
            print("JSON файл не найден")

        try:
            db.session.commit()
            print("Книги успешно импортированы!")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при сохранении в базу: {e}")


if __name__ == '__main__':
    import_books()