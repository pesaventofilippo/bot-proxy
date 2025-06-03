import requests
from json import load
from fastapi import FastAPI
from modules import maintenance

app = FastAPI()
with open("settings.json", "r") as f:
    settings = load(f)


@app.post("/bot{token}")
async def handle_update(token: str, request_body: dict):
    bot_info = next((bot for bot in settings["bots"] if bot["token"] == token), None)
    if not bot_info:
        return {"error": "Bot not found"}
    if bot_info.get("maintenance_status"):
        return maintenance.handle_update(bot_info, request_body)
    if not bot_info.get("proxy_pass"):
        return {"error": "Bot not configured"}

    url = bot_info["proxy_pass"]
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=request_body, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to forward the request"}

    return response.json()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=settings['api_host'], port=settings['api_port'])
