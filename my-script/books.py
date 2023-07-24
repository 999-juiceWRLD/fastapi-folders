from fastapi import Body, FastAPI
from typing import Union

app = FastAPI()

BOOKS = [
    {"title": "Title one", "author": "Author one", "category": "science"},
    {"title": "Title two", "author": "Author two", "category": "science"},
    {"title": "Title three", "author": "Author three", "category": "history"},
    {"title": "Title four", "author": "Author four", "category": "math"},
    {"title": "Title five", "author": "Author five", "category": "math"}
]

@app.get("/")
async def read_root():
    return {"He": "World"}

@app.get("/api-endpoint")
async def first_page():
    return {"message": "ayyo wassupp"}

@app.get("/books")
async def read_all_books():
    return BOOKS

# @app.get("/books/{idx}")
# async def get_nth_book(idx: int, q: Union[str, None]=None):
#     return {"item": BOOKS[idx], "q": q}

@app.get("/books/{book_title}")
async def read_book(book_title: str, q: Union[str, None]=None):
    for b in BOOKS:
        if b.get("title").casefold() == book_title.casefold():
            return {"result": b, "q": q}
    return {"/books/{book_title}": f" {book_title} is not found"}


@app.get("/books/")
async def read_category_by_query(category: Union[str, None]=None):
    queried_books = []
    if category == None:
        return {"result": "error — please fill search parameter like '/books/?category=math' "}
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            queried_books.append(book)
    if len(queried_books) > 0:
        return {"result": queried_books}
    return {"result": f"as not expected — {len(queried_books)} element found"}


@app.get("/books/{book_author}/")
async def get_author_with_category(book_author: str, category: str):
    queried_books = []
    for b in BOOKS:
        if (b.get("category").casefold() == category.casefold()) and (b.get("author").casefold() == book_author.casefold()):
               queried_books.append(b)
               
    if len(queried_books) > 0:
        return {"result": queried_books}
    return {"result": f"as not expected — {len(queried_books)} element found"}
         
               
@app.post("/books")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books") # consider that titles are unique
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book
            return {"success — changed to": updated_book}

    return {"error": "Book not found"}


@app.delete("/books/{book_title}")
async def delete_book_by_title(title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == title.casefold():
            del BOOKS[i]
            return {"success": title + " — deleted"}
    
    return {"error": "Book not found"}


@app.get("/get_author/{author_name}")
async def get_author_works(author: str):
    works_list = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            works_list.append(book)
    
    if len(works_list) == 0:
        return {"unf": "none found"}
    
    return {"success": works_list}
