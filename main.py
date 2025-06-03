import requests
from json import load
from fastapi import FastAPI
import prometheus_client as prom
from modules import maintenance

app = FastAPI()
app.mount("/metrics", prom.make_asgi_app())
with open("settings.json", "r") as f:
    settings = load(f)

metrics = prom.Counter(
    f"{settings['prometheus_prefix']}_requests",
    "Total number of requests received",
    labelnames=["username"]
)

@app.post("/bot{token}")
async def handle_update(token: str, request_body: dict):
    bot_info = next((bot for bot in settings["bots"] if bot["token"] == token), None)
    if not bot_info:
        return {"error": "Bot not found"}

    metrics.labels(username=bot_info["username"]).inc()
    if bot_info.get("maintenance_status", -1) >= 0:
        return maintenance.handle_update(bot_info, request_body)
    if not bot_info.get("proxy_pass"):
        return {"error": "Bot not configured"}

    url = bot_info["proxy_pass"]
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=request_body, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to forward the request"}

    return {"success": True}


def set_webhooks():
    for bot in settings["bots"]:
        url = settings['webhook_base'].format(token=bot["token"])
        response = requests.post(
            f"https://api.telegram.org/bot{bot['token']}/setWebhook",
            json={"url": url}
        )
        print(f"Webhook for @{bot['username']}: {'OK' if response.status_code == 200 else 'FAIL'}")


if __name__ == '__main__':
    import uvicorn
    set_webhooks()
    prom.disable_created_metrics()
    prom.REGISTRY.unregister(prom.GC_COLLECTOR)
    prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
    prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
    uvicorn.run(app, host=settings['api_host'], port=settings['api_port'])
