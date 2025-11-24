from fastapi import FastAPI, Request

mock_app = FastAPI()

received_posts = []

@mock_app.post("/data")
async def receive_data(request: Request):
    body = await request.json()
    received_posts.append(body)
    return {"status": "ok"}
