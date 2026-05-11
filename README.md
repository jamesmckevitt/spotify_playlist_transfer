# Spotify Playlist Transfer

A simple Python script to copy all playlists you own from one Spotify account to another.

## How it works

The script uses [Spotipy](https://spotipy.readthedocs.io/) to authenticate two Spotify user accounts through the same developer app. It then:

1. Fetches every playlist owned by the source account.
2. For each playlist, reads all track URIs.
3. Creates a matching playlist on the destination account and adds the tracks in batches.

Both accounts authorise through a standard OAuth browser flow - you paste a redirect URL back into the terminal, so no passwords are ever handled by the script.

## Requirements

- Python 3.8+
- [Spotipy](https://pypi.org/project/spotipy/)

Install the dependency:

```bash
pip install spotipy
```

## Setup: Create a Spotify Developer App

You only need one Spotify app - it can be created under either account and will be used to authenticate both. Use whichever account is easiest to log into the developer dashboard with.

1. Go to [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and log in with either of your Spotify accounts.
2. Click **Create app**.
3. Fill in any name and description.
4. Set the **Redirect URI** to exactly: `http://127.0.0.1:8888/callback`
5. Save the app, then open its settings and note your **Client ID** and **Client Secret**.

## Configuration

Open `spotify_transfer.py` and fill in your Client ID and Client Secret at the top of the file:

```python
CLIENT_ID     = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
```

**Do not commit the file with your real credentials in it.**

## Usage

```bash
python spotify_transfer.py
```

The script will guide you through two authorisation steps:

**Step 1 - Old account:**
- A URL is printed. Open it in a browser and log in with your **source** Spotify account.
- After authorising, your browser will redirect to `http://127.0.0.1:8888/callback?code=...` (the page will show an error - that's fine).
- Copy the full URL from your browser's address bar and paste it into the terminal.

**Step 2 - New account:**
- Repeat the same process, this time logging in with your **destination** Spotify account.

The script then transfers all your playlists automatically.

## Notes

- Only playlists owned by you on the source account are transferred (not playlists you follow).
- Playlists with no transferable tracks (e.g. fully local files) are skipped.
- Playlist order, name, description, and public/private status are preserved.
- Tracks are added in batches of 100 to respect Spotify API limits.
- Token cache files (`.cache_old`, `.cache_new`) are created locally so you don't need to re-authorise if you re-run the script.