# 🔔 YTbell
**Your YouTube-to-Discord notifier.** Ping your server the second a new video drops. 

![Discord](https://img.shields.io/badge/Discord-Bot-5865F2?style=flat&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)
![Open Source](https://img.shields.io/badge/Open_Source-Yes-success?style=flat)

With **YTbell** you can notify your community the recent video of your *favorite* channel.

## ✨ Features
- ⚡ **Lightning Fast:** Uses RSS feeds to detect new videos almost instantly.
- 🛡️ **Built-in Shorts Filter:** Automatically detects and ignores YouTube Shorts.
- 🎯 **Smart Channel Detection:** Just type `channel link` and the bot will find the hidden channel ID for you.
- 💻 **100% Open Source:** Host it yourself or use our public instance.
- 🌈 **Customizable:** You can build your own bot by integrating YTbell's features. 

## ⌨️​ Commands
 - **Command On-Demand:** Use `!lv` to see the last video.
 - **Set youtube channel:** Use `!setytchannel <url>` to set your favorite channel.
 - **Set text channel:** Use `!setcanal` to set where you want to receive notifications.  

---

## 🚀 How to use YTbell

### Option A: Invite the public bot (No coding required)
Want YTbell in your server right now? Just click the link below to authorize the bot:
> **[👉 Click here to invite YTbell to your Discord Server](https://discord.com/oauth2/authorize?client_id=1486040335716188192&permissions=8&integration_type=0&scope=bot)**

### Option B: Host it yourself (For Developers)
Want to create a custom version for your favorite YouTuber? Clone this repo and run it yourself!

**1. Prerequisites:**
You will need Python 3.8+ and a Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications).
*⚠️ Make sure to enable the **Message Content Intent** in the Bot tab!*

**2. Installation:**
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/YTbell.git](https://github.com/YOUR_USERNAME/YTbell.git)
cd YTbell

# Install the required libraries
pip install -r requirements.txt
```

**3. Hosting:**
**[Railway](https://railway.com/)** 
**[Tutorial](https://www.figma.com/board/zZ7AVRpSNeVfhXknIk5fsv/Railway-tutorial?node-id=0-1&t=nsBlD8iNSfCQxBpt-1)**

### Example of a bot created from YTbell
**[ADObell](https://github.com/EricBatalla12/ADObell)**