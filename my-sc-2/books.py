from fastapi import Body, FastAPI, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, Union

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: float
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(title="id is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    rating: float = Field(ge=0, le=5)
    published_date: int = Field(ge=1999, le=2023)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "deneme title",
                "author": "steven spielberg",
                "description": "this is going to be filmed too",
                "rating": 4.9,
                "published_date": 2021
            }
        }
    

BOOKS = [
    Book(1, "Kısa Çin Tarihi", "Linda Jaivin", "From a little tribe to a super power...", 4.3, 1999),
    Book(2, "Dört Talmud Okuması", "Emmanuel Levinas", "İsrailin sözlüğü geleneğinin notl...", 3.9, 2023),
    Book(3, "Evrimci Politik İktisat", "Adem Levent", "İktisat, yaklaşık 150 yıldır doğa b...", 4.1, 2003),
    Book(4, "Anayasal Gelişme Tezleri", "Bülent Tanör", "Bülent Tanör'ün 1977 Yunus Nadi ya...", 4.9, 2008),
    Book(5, "İkinci Dünya Savaşı: İnfografik", "Jean Lopez", "World War II: Infographics", 4.6, 1992),
    Book(6, "Introduction to French", "Jane Doe", "This book is going to have you int...", 3.2, 2017)
]


@app.get("/books")
def get_all_books():
    return BOOKS

@app.get("/books/{bookid}")
def get_book_with_id(bookid: int):
    for b in BOOKS:
        if b.id == bookid:
            return b
    return {"error": "olmadı ağabey"}

@app.get("/books/")
def get_by_rating_or_higher(rating: Union[float, int]):
    books_returned = []
    for b in BOOKS:
        if b.rating >= rating:
            books_returned.append(b)
    return books_returned

    
@app.get("/books/published/")
def get_by_year_or_higher(pd: int):
    books_returned = []
    for b in BOOKS:
        if b.published_date >= pd:
            books_returned.append(b)
    if len(books_returned) > 0:
        return {"books": books_returned, "query param pd": pd}
    else:
        return {"error": f"no such book found published later than {pd}"}
    
@app.post("/books")
def create_book(new_book:BookRequest):
    book_request = Book(**new_book.dict())
    BOOKS.append(find_book_id(book_request))

def find_book_id(book: Book):
    book.id = BOOKS[-1].id + 1 if len(BOOKS) > 0 else 1
    return book

def change_content(i: int, id: int, book:BookRequest):
    book.id = id
    BOOKS[i] = book
    return book
    

@app.put("/books/{bookid}")
def change_book(bookid: int, updated:BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == bookid:
            BOOKS[i] = change_content(i, bookid, updated)
            # return {"success": "updated"}
            return BOOKS[i]
    return {"index error": "no such element"}

@app.delete("/books/{bookid}")
def delete_book_with_id(bookid: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == bookid:
            del BOOKS[i]
            return {"deleted": "successfully"}
    return {"no such": "element"}


"""

Path() for path parameters
Query() for query parameters

they both used inside the declared function parentheses (as parameters)
like inline css they got higher priority
"""