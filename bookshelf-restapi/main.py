from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "Bookshelf!"}


@app.get("/books")
async def read_books():
    return [
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee"},
        {"title": "1984", "author": "George Orwell"},
    ]

@app.get("/books/{book_id}")
async def read_book(book_id: int):
    return {"book_id": book_id, "book": book}
