import gzip

import re

import urllib.request

from pathlib import Path

PLAYLIST_URL = "https://biskyt.github.io/legalFreeIPTVplaylist/live.m3u"

EPG_URL = "https://biskyt.github.io/legalFreeIPTVplaylist/epg.xml.gz"

OUT = Path("site")

OUT.mkdir(exist_ok=True)

def fetch(url):

    request = urllib.request.Request(

        url, headers={"User-Agent": "Mozilla/5.0"}

    )

    with urllib.request.urlopen(request, timeout=60) as response:

        return response.read()

playlist = fetch(PLAYLIST_URL).decode("utf-8", errors="replace")

epg = fetch(EPG_URL)

if playlist.startswith("\ufeff"):

    playlist = playlist[1:]

if not playlist.lstrip().startswith("#EXTM3U"):

    raise ValueError("The downloaded playlist is not a valid M3U file.")

# Save the complete playlist

(OUT / "all-live.m3u").write_text(playlist, encoding="utf-8")

# Build a sports-only playlist

lines = playlist.splitlines()

sports = ["#EXTM3U"]

for i, line in enumerate(lines):

    if line.startswith("#EXTINF"):

        group = re.search(r'group-title="([^"]*)"', line)

        if group and "sport" in group.group(1).lower():

            sports.append(line)

            if i + 1 < len(lines):

                sports.append(lines[i + 1])

(OUT / "sports.m3u").write_text(

    "\n".join(sports) + "\n", encoding="utf-8"

)

# Validate and save the EPG

if epg[:2] == b"\x1f\x8b":

    gzip.decompress(epg)

(OUT / "epg.xml.gz").write_bytes(epg)

print("UHF playlists and EPG built successfully.")
