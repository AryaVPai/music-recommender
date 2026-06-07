from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommender import recommend_by_song, recommend_by_mood

app = FastAPI()

# This lets your React frontend talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request models ---
class SongRequest(BaseModel):
    song_name: str
    n: int = 10

class MoodRequest(BaseModel):
    mood: str
    genre: str = None
    english_only: bool = False
    n: int = 10

# --- Endpoints ---
@app.get("/")
def root():
    return {"message": "Music Recommender API is running"}

@app.post("/recommend/song")
def recommend_song(request: SongRequest):
    results = recommend_by_song(request.song_name, request.n)
    if results is None:
        raise HTTPException(status_code=404, 
                           detail=f"Song '{request.song_name}' not found")
    return {"recommendations": results}

@app.post("/recommend/mood")
def recommend_mood(request: MoodRequest):
    results = recommend_by_mood(
        request.mood, request.genre, 
        request.english_only, request.n
    )
    if results is None:
        raise HTTPException(status_code=404, 
                           detail="No songs found for those filters")
    return {"recommendations": results}