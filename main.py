from typing import Annotated
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi import FastAPI, Depends
import uvicorn

app = FastAPI()

engine = create_async_engine("sqlite+aiosqlite:///books.db")

new_session = async_sessionmaker(engine, expire_on_commit=False) 

async def get_session():
    async with new_session() as session:  
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase): 
    pass

class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]


@app.post("/setup_db")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return {"message": "Database setup"}


class BookAddSchema(BaseModel):
    title: str
    author: str

class BookSchema(BookAddSchema):
    id: int

@app.post("/books")
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(
        title = data.title,
        author = data.author
    )
    session.add(new_book)
    await session.commit()
    return {"ok": True}

@app.get("/books")
async def get_books(session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    return result.scalars().all()

@app.put("/books/{book_id}")
async def update_books(book_id: int, data: BookAddSchema, session: SessionDep):
    query = select(BookModel).where(BookModel.id == book_id)
    result = await session.execute(query)
    book = result.scalars().one()
    book.title = data.title
    book.author = data.author
    await session.commit()
    return {"ok": True}

@app.delete("/books/{book_id}")
async def delete_books(book_id: int, session: SessionDep):
    query = select(BookModel).where(BookModel.id == book_id)
    result = await session.execute(query)
    book = result.scalars().one()
    await session.delete(book)
    await session.commit()
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app)