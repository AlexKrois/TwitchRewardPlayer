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

---

## 🖥 Setup

1. Set every value in the .env file.

2. In OBS, add a **Browser Source** named like:

```
YTVideo
```
It doesn't matter what you set the name to, you will get asked about the name after.

Also, if you've entered a wrong name you can delete the line REWARD_ID=xxxx in the .env file and you will get asked again.

3. Set the URL to:

```
file:///absolute/path/to/embed.html
```

4. In main.py change the host and port to whatever you need:
```
cl = obs.ReqClient(host="127.0.0.1", port=4444)
```
172.26.32.1 is the default IP if you're on WSL.
The port can be found in OBS (Tools -> Websocket Settings) - should be 4444 by default.

---

## ▶️ Running the script

Simply run:

```bash
python3 main.py
```

The script will:

1. Connect to Twitch EventSub WebSocket
2. Subscribe to redemptions
3. Wait for viewer submissions
4. When a YouTube link is submitted:

   * Extract video ID & timestamp
   * Get duration from YouTube API
   * Create `embed.html`
   * Show the video in OBS
   * Hide it after playback

---

## 🧪 Example Workflow

Viewer redeems a reward with:

```
https://youtu.be/dQw4w9WgXcQ?t=43
```

Script does:

* Extracts video ID: `dQw4w9WgXcQ`
* Gets duration
* Limits playback to ~40 seconds
* Writes an embed iframe to `embed.html`
* Shows the OBS browser source
* Sleeps until video ends
* Clears the file
* Hides the browser source again

No interaction needed on your side.

---

## 📄 License

MIT License — free to use, modify, and share.

