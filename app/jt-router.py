from fastapi import FastAPI, Request, status, responses
import httpx
import os

app = FastAPI()

bot_token = os.getenv("BOT_TOKEN", "NOT_SET")
channel_id = "-1002576265108"

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    notification_type = data.get("NotificationType")
    
    message = None

    print(data)

    if notification_type == 'PlaybackStart':
        
        message = ""
        
        if data.get('ItemType') == 'Episode':
            message = f"▶️ {data.get('SeriesName')} - S{data.get('SeasonNumber00')}E{data.get('EpisodeNumber00')} - {data.get('Name')}\n"
        else:
            message = f"▶️ {data.get('Name')}\n"
        
        message = message + (
            f"👤 {data.get('NotificationUsername')}\n"
            f"🖥️ {data.get('DeviceName')}\n"
            f"🐵 {data.get('ClientName')}\n"
            f"🚀 {data.get('PlayMethod')}"
        )
    elif notification_type == 'PlaybackStop':

        message = ""

        if data.get('ItemType') == 'Episode':
            message = f"⏹️ {data.get('SeriesName')} - S{data.get('SeasonNumber00')}E{data.get('EpisodeNumber00')} - {data.get('Name')}\n"
        else:
            message = f"⏹️ {data.get('Name')}\n"

        message = message + (
            f"👤 {data.get('NotificationUsername')}\n"
            f"🖥️ {data.get('DeviceName')}\n"
            f"🐵 {data.get('ClientName')}"
        )
    elif notification_type == 'SessionStart':
        message = (
            f"⚡ User active\n"
            f"👤 {data.get('NotificationUsername')}\n"
            f"🖥️ {data.get('DeviceName')}\n"
            f"🐵 {data.get('ClientName')}\n"
            f"🛡️ {data.get('RemoteEndPoint')}"
        )
    elif notification_type == 'AuthenticationSuccess':
        message = (
            f"🔑 Auth\n"
            f"👤 {data.get('NotificationUsername')}\n"
            f"🖥️ {data.get('DeviceName')}\n"
            f"🐵 {data.get('ClientName')}\n"
            f"🛡️ {data.get('RemoteEndPoint')}"
        )
    elif notification_type == 'AuthenticationFailure':
        message = (
            f"❌ Auth\n"
            f"👤 {data.get('NotificationUsername')}\n"
            f"🖥️ {data.get('DeviceName')}\n"
            f"🐵 {data.get('ClientName')}\n"
            f"🛡️ {data.get('RemoteEndPoint')}"
        )
    elif notification_type == 'PendingRestart':
        message = (
            f"⚠️ Server Restart Pending"
        )
    elif notification_type == 'TaskCompleted':
        message = (
            f"✅ Server Task Completed"
        )
    elif notification_type == 'UserLockedOut':
        message = (
            f"⛔ User Locked Out\n"
            f"👤 {data.get('NotificationUsername')}\n"
        )
    elif notification_type == 'ItemAdded':
        if data.get('ItemType') == 'Movie':
            message = (
                f"⚡ Movie Added\n"
                f"🎞️ {data.get('Name')}\n"
                f"{data.get('Year')}\n"
                f"{data.get('Genres')}\n"
                f"https://www.imdb.com/title/{data.get('Provider_imdb')}/\n"
                f"{data.get('Overview')}"
            )
        elif data.get('ItemType') == 'Episode':
            message = (
                f"⚡ TV Episode Added\n"
                f"📺 {data.get('SeriesName')} - S{data.get('SeasonNumber00')}E{data.get('EpisodeNumber00')} - {data.get('Name')}\n"
                f"{data.get('Year')}\n"
                f"{data.get('Genre')}\n"
                f"https://www.imdb.com/title/{data.get('Provider_imdb')}/\n"
                f"{data.get('Overview')}"
            )
        else:
            message = (
                f"⚡ Item Added\n"
            )
    elif notification_type == 'ItemDeleted':
        if data.get('ItemType') == 'Movie':
            message = (
                f"⚡ Movie Removed\n"
                f"🎞️ {data.get('Name')}\n"
            )
        elif data.get('ItemType') == 'Episode':
            message = (
                f"⚡ TV Episode Removed\n"
                f"📺 {data.get('SeriesName')} - S{data.get('SeasonNumber00')}E{data.get('EpisodeNumber00')} - {data.get('Name')}"
            )
        else:
            message = (
                f"⚡ Item Removed\n"
            )
    else:
        print(f"unhandled Notification Type: {notification_type}")
        print(data)
        return responses.JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                      content={"text": f"unhandled notification type {notification_type}"})

    

    async with httpx.AsyncClient() as client:
        
        if notification_type in ('ItemAdded'):
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": channel_id,
                    "photo": f"{data.get('ServerUrl')}/Items/{data.get('ItemId')}/Images/Primary",
                    "caption": f"{message}",
                    "parse_mode": "html"
                }
            )
        else:
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": channel_id,
                    "text": f"{message}",
                    "parse_mode": "html"
                }
            )

    if response.status_code != 200:
        print(f"error calling telegram API: {response.status_code}:{response.text}")
        return responses.JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                      content={"text": f"telegram api error {response.text}"})
    
    # return {"status_code": "200"}
    return responses.JSONResponse(status_code=status.HTTP_200_OK, content={"text": "OK"})
