

from fastapi import FastAPI, Depends ,HTTPException,Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import engine, Base, get_db
from models import Link
from schemas import ShortenRequest, LinkOut ,UpdateLinkRequest
from utils import base
from rate_limiter import rate_limit,r
from cache import get_cached_url, cache_url
app = FastAPI()


@app.get("/")
def read_root():
    return{"message":"Hello world"}

@app.post(
    "/shorten",
    response_model=LinkOut,
    dependencies=[Depends(rate_limit)]
)
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
 if payload.custom_alias:
    statement = select(Link).where(
        Link.short_code == payload.custom_alias
    )
    existing_link = db.execute(statement).scalar_one_or_none()

    if existing_link:
        raise HTTPException(
            status_code=409,
            detail="This custom alias is already taken",
        )

    link = Link(
        original_url=str(payload.url),
        short_code=payload.custom_alias,
    )
    db.add(link)

 else:
    link = Link(original_url=str(payload.url))
    db.add(link)
    db.flush()

    link.short_code = base(link.id)

 db.commit()
 db.refresh(link)

 return link



@app.get("/links", response_model=list[LinkOut])
def get_links(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    statement = (
        select(Link)
        .order_by(Link.id)
        .limit(limit)
        .offset(offset)
    )
    links = db.execute(statement).scalars().all()
    return links

@app.get("/links/{code}", response_model=LinkOut)
def get_link(code: str, db: Session = Depends(get_db)):
    statement = select(Link).where(Link.short_code == code)
    link = db.execute(statement).scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return link


@app.put("/links/{code}", response_model=LinkOut)
def update_link(
    code: str,
    payload: UpdateLinkRequest,
    db: Session = Depends(get_db)
):
    statement = select(Link).where(Link.short_code == code)
    link = db.execute(statement).scalar_one_or_none()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    link.original_url = str(payload.url)

    db.commit()
    db.refresh(link)

    r.delete(f"url:{code}")  # Invalidate the cached URL

    return link

@app.delete("/links/{code}")
def delete_link(code: str, db: Session = Depends(get_db)):
    statement = select(Link).where(Link.short_code == code)
    link = db.execute(statement).scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=404, detail="URL not found")

    db.delete(link)
    db.commit()
    r.delete(f"url:{code}")

    return {"message": "URL deleted successfully"}


@app.get("/{code}")
def get_code(code: str, db: Session = Depends(get_db)):

    
    cached_url = get_cached_url(code)

    
    if cached_url:
        print("Cache hit")
        return RedirectResponse(url=cached_url, status_code=307)

    
    link = db.query(Link).filter(Link.short_code == code).first()

    if link is None:
        raise HTTPException(status_code=404, detail="URL not found")

   
    cache_url(code, link.original_url)

    return RedirectResponse(url=link.original_url, status_code=307)
