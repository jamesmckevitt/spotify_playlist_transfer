import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# ---------------------------------------------------------------------------
# Configuration -- fill in your Client ID and Secret from:
# https://developer.spotify.com/dashboard
# ---------------------------------------------------------------------------
CLIENT_ID     = ""
CLIENT_SECRET = ""
REDIRECT_URI  = "http://127.0.0.1:8888/callback"

SCOPE = (
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-public "
    "playlist-modify-private"
)

if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit(
        "ERROR: Fill in CLIENT_ID and CLIENT_SECRET at the top of this script."
    )


def authorise(label, cache_path):
    """Open an OAuth flow for one Spotify account and return an authenticated client."""
    auth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=cache_path,
        open_browser=False,
    )
    print(f"\nOpen this URL in a browser and log in with your {label} Spotify account:\n")
    print("  " + auth.get_authorize_url() + "\n")
    redirected = input("Paste the full redirect URL here: ").strip()
    code = auth.parse_response_code(redirected)
    auth.get_access_token(code, as_dict=False)
    return spotipy.Spotify(auth_manager=auth)


print("=== Spotify Playlist Transfer ===")

print("Step 1: Authorise your OLD account")
old_sp = authorise("OLD", ".cache_old")
old_user = old_sp.current_user()
print("Logged in as:", old_user["display_name"], "(" + old_user["id"] + ")\n")

print("Fetching all playlists from old account...")
playlists = []
results = old_sp.current_user_playlists(limit=50)
while results:
    for item in results["items"]:
        if item["owner"]["id"] == old_user["id"]:
            playlists.append(item)
    results = old_sp.next(results) if results["next"] else None
print("Found", len(playlists), "playlists owned by you.\n")

print("Step 2: Authorise your NEW account")
new_sp = authorise("NEW", ".cache_new")
new_user = new_sp.current_user()
print("Logged in as:", new_user["display_name"], "(" + new_user["id"] + ")\n")

transferred = 0
skipped = 0

for i, playlist in enumerate(playlists, 1):
    name        = playlist["name"]
    description = playlist.get("description", "")
    public      = playlist.get("public", False)
    playlist_id = playlist["id"]

    print(f"[{i}/{len(playlists)}] Transferring: {name}")

    tracks = []
    results = old_sp.playlist_items(playlist_id, limit=100)
    while results:
        for item in results["items"]:
            if item.get("item") and item["item"].get("id"):
                tracks.append(item["item"]["uri"])
        results = old_sp.next(results) if results["next"] else None

    print("  ", len(tracks), "tracks found.")

    if not tracks:
        print("  Skipping (empty playlist).\n")
        skipped += 1
        continue

    new_playlist = new_sp._post(
        "me/playlists",
        payload={"name": name, "public": public, "description": description},
    )
    new_playlist_id = new_playlist["id"]

    for j in range(0, len(tracks), 100):
        batch = tracks[j : j + 100]
        new_sp.playlist_add_items(new_playlist_id, batch)
        time.sleep(0.2)

    print("  Done!\n")
    transferred += 1

print("=== Transfer complete! ===")
print(f"Transferred {transferred} playlists, skipped {skipped} empty playlists.")
print(f"Destination account: {new_user['display_name']}")
