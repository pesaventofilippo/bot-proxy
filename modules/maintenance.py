from json import load

with open("maintenance.json", "r") as f:
    settings = load(f)


def status_message(status: int) -> str:
    message = settings["messages"].get(str(status), "2")
    contacts = [f"{i['icon']} <a href=\"{i['url']}\">{i['title']}</a>" for i in settings["contacts"]]

    return (f"{message['icon']} <b>{message['title']}</b>\n\n"
            f"🇬🇧 {message['en']}\n\n"
            f"🇮🇹 {message['it']}\n\n"
            f"{'\n'.join(contacts)}")


def handle_update(bot_info: dict, request_body: dict) -> dict:
    if "message" not in request_body:
        return {"success": True} # ignore non-message updates

    return {
        "method": "sendMessage",
        "chat_id": request_body["message"]["chat"]["id"],
        "text": status_message(bot_info["maintenance_status"]),
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
