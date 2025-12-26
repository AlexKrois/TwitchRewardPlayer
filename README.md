# Twitch OBS YouTube Reward Player

This script listens for **Twitch Channel Point Redemptions** and automatically plays **YouTube videos** that got submitted via the Channel Point Redemption.

---

## ✨ Features

* Listens for specific Channel Point Redemptions
* Plays the video, that was submitted in the Redemption in a Browser-Source
* You can set a max. allowed time
* It just plays a fucking video on OBS man
* Just read the code, its literally so easy to understand

https://github.com/user-attachments/assets/2ee7e84f-2e6f-4a0a-869a-1c0eb59900df


---

## 🧰 Requirements

* pip install -r requirements.txt

---

## ⚙️ IMPORTANTE!!!!! Environment Variables

| Variable               | Where to find it                                                           |
| ---------------------- | -------------------------------------------------------------------------- |
| `TWITCH_CLIENT_ID`     | https://dev.twitch.tv/console/apps                                         |
| `TWITCH_CLIENT_SECRET` | https://dev.twitch.tv/console/apps                                         |
| `TWITCH_CHANNEL_ID`    | https://api.ivr.fi/v2/twitch/user?id=&login=alexvcs change alexvcs         |
| `TWITCH_USER_TOKEN`    | https://dev.twitch.tv/docs/authentication/getting-tokens-oauth             |
| `YOUTUBE_API_KEY`      | https://console.cloud.google.com/apis/api/youtube.googleapis.com/          |
| `BROWSER_SOURCE_NAME`  | Just the name of the browser source you create in OBS                      |

---

## 🖥 Setup

1. Populate every value in the .env file correctly.

2. In OBS, add a **Browser Source** named like:

```
YTVideo
```

3. Set the URL to:

```
file:///absolute/path/to/embed.html
```

4. In main.py change the host and port to whatever you need:

    **172.26.32.1** is the default IP if you're on **WSL**.

    The **port** can be found in **OBS (Tools -> Websocket Settings)** - should be 4444 by default.
```
cl = obs.ReqClient(host="127.0.0.1", port=4444)
```

5. Create a redemption, that is **redeemable with user input** and copy / remember the name of it


---

## ▶️ Running the script

Simply run:

```bash
python3 main.py
```

If it's your first time running the script, you will be asked to enter the redemption name - just paste it in and press enter.

You can delete the line "REWARD_ID=xxxx" from the .env file, to get asked about the redemption name again.

---

## 🧪 Configurations

- MAX_VIDEO_DURATION_SECONDS
  - Maximum length of the video.
  - If the video is shorter than MAX_VIDEO_DURATION_SECONDS, the whole video will play.
  - If the video is longer than MAX_VIDEO_DURATION_SECONDS, the video will play for MAX_VIDEO_DURATION_SECONDS + 3 seconds (buffer time).


- BUFFER_TIME_SECONDS
  - Extra time as a buffer for OBS to load the browser source / video.
  - If set to 0, the video may get cut off at the end, because it took a couple of seconds in the beginning to load.
  - If set to high, the finished video / browser source will stay visible on screen. 

---

## 📄 License

MIT License — free to use, modify, and share.

