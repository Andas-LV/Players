from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy import nulls_last
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Player
import schemas

router = APIRouter()

@router.get("/", response_model=Page[schemas.PlayerBase])
async def get_players(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    players = db.query(Player).offset(offset).limit(limit).all()
    return paginate(players)

@router.get("/search", response_model=Page[schemas.PlayerBase])
async def search_players(name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Player)
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))
    players = query.all()
    return paginate(players)

@router.get("/byRating", response_model=Page[schemas.PlayerBase])
async def get_players_by_rating(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    players = db.query(Player).order_by(nulls_last(Player.overall_rating.desc())).offset(offset).limit(limit).all()
    return paginate(players)

@router.get("/byPrice", response_model=Page[schemas.PlayerBase])
async def get_players_by_price(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    players = db.query(Player).order_by(nulls_last(Player.value_euro.desc())).offset(offset).limit(limit).all()
    return paginate(players)

@router.get("/{player_id}", response_model=schemas.PlayerBase)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player