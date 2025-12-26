import time
import obsws_python as obs
import asyncio
import json
import os
import requests
import websockets
import re
import dotenv


def get_app_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, params=params)
    resp.raise_for_status()
    return resp.json()["access_token"]


def is_youtube_url(url):
    youtube_regex = re.compile(
        r"(https?://)?(www\.)?"
        r"(youtube\.com|youtu\.be)/"
        r"((watch\?v=|shorts/|embed/|playlist\?list=)?[A-Za-z0-9_\-]{11,}|playlist\?list=[A-Za-z0-9_\-]+)"
    )
    return bool(youtube_regex.search(url))


def extract_start_time_seconds(url):
    match = re.search(r"[?&](?:t|start)=(\d+m)?(\d+s?|\d+)?", url, re.IGNORECASE)
    if match:
        total = 0
        minutes = match.group(1) or ""
        seconds = match.group(2) or ""
        if minutes:
            m = int(minutes.replace("m", ""))
            total += m * 60
        if seconds:
            sec_str = seconds.replace("s", "")
            if sec_str.isdigit():
                total += int(sec_str)
        return total
    return 0


def get_reward_id(reward_title):
    url = f"https://api.twitch.tv/helix/channel_points/custom_rewards"
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {USER_ACCESS_TOKEN}"}
    params = {"broadcaster_id": CHANNEL_ID}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    rewards = resp.json().get("data", [])
    for reward in rewards:
        if reward.get("title") == reward_title:
            return reward.get("id")
    return None


def get_youtube_video_duration_seconds(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {"id": video_id, "part": "contentDetails", "key": YOUTUBE_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return None
    duration_str = items[0]["contentDetails"]["duration"]

    match = re.match(r"PT((\d+)H)?((\d+)M)?((\d+)S)?", duration_str)
    total_seconds = 0
    if match:
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(4)) if match.group(4) else 0
        seconds = int(match.group(6)) if match.group(6) else 0
        total_seconds = hours * 3600 + minutes * 60 + seconds
    else:
        return MAX_VIDEO_DURATION_SECONDS
    return total_seconds


async def listen_rewards():
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {USER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    async with websockets.connect("wss://eventsub.wss.twitch.tv/ws") as ws:
        print("Connected to Twitch EventSub WebSocket.")
        session_id = None

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data["metadata"]["message_type"] == "session_welcome":
                session_id = data["payload"]["session"]["id"]

                sub_payload = {
                    "type": "channel.channel_points_custom_reward_redemption.add",
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": CHANNEL_ID,
                    },
                    "transport": {"method": "websocket", "session_id": session_id},
                }
                if REWARD_ID:
                    sub_payload["condition"]["reward_id"] = REWARD_ID

                sub_resp = requests.post(
                    "https://api.twitch.tv/helix/eventsub/subscriptions",
                    headers={**headers, "Content-Type": "application/json"},
                    data=json.dumps(sub_payload),
                )
                if sub_resp.status_code != 202:
                    print("Subscription failed:", sub_resp.text)

            elif data["metadata"]["message_type"] == "notification":
                event = data["payload"]["event"]
                user = event["user_name"]
                user_input = event.get("user_input", "")
                embed_url = ""

                if is_youtube_url(user_input):
                    yt_match = re.search(
                        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_\-]{11})",
                        user_input,
                    )
                    if yt_match:
                        video_id = yt_match.group(1)

                        duration = get_youtube_video_duration_seconds(video_id)
                        if duration is None:
                            print("No duration")
                            continue
                        if duration > MAX_VIDEO_DURATION_SECONDS:
                            # Just to be safe, MAX + 3 seconds buffer
                            duration = MAX_VIDEO_DURATION_SECONDS + 3
                        else:
                            duration += 3

                        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&controls=0&start={extract_start_time_seconds(user_input)}&end={duration}"

                        embedding = f'<iframe src="{embed_url}" title="YouTube video player" frameborder="0" allow="encrypted-media; autoplay" referrerpolicy="strict-origin-when-cross-origin" style="width:100vw; height:100vh; position:fixed; top:0; left:0; border:none; z-index:9999;" allowfullscreen></iframe>'
                        with open("embed.html", "w") as f:
                            f.write(embedding)

                        cl.set_scene_item_enabled(
                            str(cl.get_current_program_scene().scene_name),  # type: ignore
                            cl.get_scene_item_id(str(cl.get_current_program_scene().scene_name), BROWSER_SOURCE_NAME).scene_item_id,  # type: ignore
                            True,
                        )

                        time.sleep(duration)

                        with open("embed.html", "w") as f:
                            f.write("")

                        cl.set_scene_item_enabled(
                            str(cl.get_current_program_scene().scene_name),  # type: ignore
                            cl.get_scene_item_id(str(cl.get_current_program_scene().scene_name), BROWSER_SOURCE_NAME).scene_item_id,  # type: ignore
                            False,
                        )

                else:
                    print("Not a YouTube URL.")
                print(f"{user} with {embed_url} is done")

            elif data["metadata"]["message_type"] == "session_keepalive":
                pass


if __name__ == "__main__":
    while True:
        try:
            cl = obs.ReqClient(host="172.26.32.1", port=4444)

            if dotenv.load_dotenv():
                CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
                CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
                CHANNEL_ID = os.getenv("TWITCH_CHANNEL_ID")
                USER_ACCESS_TOKEN = os.getenv("TWITCH_USER_TOKEN")
                YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
                BROWSER_SOURCE_NAME = os.getenv("BROWSER_SOURCE_NAME")
                REWARD_ID = os.getenv("REWARD_ID")
                if REWARD_ID is None:
                    REWARD_ID = get_reward_id(input("Enter the reward title: "))
                    with open(".env", "a") as env_file:
                        env_file.write(f"\nREWARD_ID={REWARD_ID}\n")
                if (
                    CLIENT_ID is None
                    or CLIENT_SECRET is None
                    or CHANNEL_ID is None
                    or USER_ACCESS_TOKEN is None
                    or YOUTUBE_API_KEY is None
                    or BROWSER_SOURCE_NAME is None
                ):
                    raise Exception("Missing required environment variables")
            else:
                raise Exception("Failed to load .env file")

            MAX_VIDEO_DURATION_SECONDS = 45

            asyncio.run(listen_rewards())
        except KeyboardInterrupt:
            print("Program interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Restarting in 5 seconds...")
            time.sleep(5)
