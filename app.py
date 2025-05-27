from fastapi import FastAPI, Request
from services.recommender import recommend

app = FastAPI()

@app.post("/recommend")
async def get_recommendation(request: Request):
    user_input = await request.json()
    result = recommend(user_input)
    return {"recommendations": result}