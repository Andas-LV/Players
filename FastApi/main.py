from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.player_routes import router as player_router
from routes.user_routes import router as user_router
from fastapi_pagination import add_pagination

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(player_router, prefix="/players", tags=["Players"])
app.include_router(user_router, prefix="", tags=["User"])

add_pagination(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
