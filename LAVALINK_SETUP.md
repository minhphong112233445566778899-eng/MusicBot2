# Lavalink Configuration Guide

## Issue: Lavalink Connection Failed

If you're seeing errors like:
```
An unexpected error occurred while connecting Node to Lavalink: "89.106.84.59/v4/websocket"
```

## Root Cause
Your `LAVALINK_URI` environment variable is missing the protocol (`http://` or `https://`) and possibly the port.

## ✅ Correct Format

### For HTTP (most common):
```env
LAVALINK_URI=http://89.106.84.59:2333
LAVALINK_PASSWORD=your_password_here
```

### For HTTPS:
```env
LAVALINK_URI=https://89.106.84.59:443
LAVALINK_PASSWORD=your_password_here
```

## ❌ Wrong Format
```env
LAVALINK_URI=89.106.84.59  ← Missing protocol and port!
```

## Quick Fix for Railway:

1. Go to your Railway project
2. Click on your bot service
3. Go to **Variables** tab
4. Update `LAVALINK_URI` to include `http://` and port `:2333`
5. Example: `http://89.106.84.59:2333`
6. Save and redeploy

## Public Lavalink Servers

If your Lavalink server isn't working, try these public ones:

### Option 1:
```env
LAVALINK_URI=https://lavalink.devamop.in
LAVALINK_PASSWORD=DevamOP
```

### Option 2:
```env
LAVALINK_URI=https://lavalink-repl.mrjokerat.repl.co
LAVALINK_PASSWORD=www.jokerat.ga
```

### Option 3:
```env
LAVALINK_URI=https://lavalink.oops.wtf
LAVALINK_PASSWORD=www.freelavalink.ga
```

**Note:** Public servers may have rate limits or downtime. For production, host your own!

## Slash Commands Will Still Work!

Good news: I've updated the bot to sync slash commands **before** connecting to Lavalink.

This means:
- ✅ Slash commands will register even if Lavalink fails
- ✅ You can see and use `/help` command
- ⚠️ Music playback won't work until Lavalink is connected
- ✅ Once you fix the URI, music commands will work

## Expected Logs (Success):

```
Logged in as YourBot#1234
✅ Slash commands synced!
✅ Connected to Lavalink!
✅ Lavalink node main is ready!
Connected to 1 guild(s)
```

## How to Host Your Own Lavalink

See the main README.md for instructions on hosting Lavalink with Docker or Railway.
