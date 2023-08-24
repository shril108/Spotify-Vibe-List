import time
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import random
from functools import reduce
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy import oauth2
from bottle import route, run, request


SPOTIPY_CLIENT_ID = "a77d4744434b4f81a84e3c7463402eeb"
SPOTIPY_CLIENT_SECRET = "068628f43c1e413c845cbed1deabaad1"
SPOTIPY_REDIRECT_URI = "https://localhost:8888/callback"
CACHE = '.spotipyoauthcache'
# username = 'Meliodas'

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


# token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri=redirect_uri)

# if token:
#     sp = spotipy.Spotify(auth=token)
# else:
#     print("Can't get token for", username)



playlists = sp.user_playlists('spotify')
spotify_playlist_ids = []
while playlists:
    for i, playlist in enumerate(playlists['items']):
        spotify_playlist_ids.append(playlist['uri'][-22:])
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
spotify_playlist_ids[:20]

ids = []

def getTrackIDs(playlist_id):
    playlist = sp.user_playlist('spotify', playlist_id)
    for item in playlist['tracks']['items'][:50]:
        track = item['track']
        if track == None: continue
        ids.append(track['id'])
    return

def getTrackFeatures(track_id):
  meta = sp.track(track_id)
  features = sp.audio_features(track_id)

  # meta
  track_id = track_id
  name = meta['name']
  album = meta['album']['name']
  artist = meta['album']['artists'][0]['name']
  release_date = meta['album']['release_date']
  length = meta['duration_ms']
  popularity = meta['popularity']
  if meta['album']['genres']:
    genres = meta['album']['genres']
  else:
      genres = ""

  # features
  acousticness = features[0]['acousticness']
  danceability = features[0]['danceability']
  energy = features[0]['energy']
  instrumentalness = features[0]['instrumentalness']
  liveness = features[0]['liveness']
  loudness = features[0]['loudness']
  speechiness = features[0]['speechiness']
  tempo = features[0]['tempo']
  time_signature = features[0]['time_signature']

  track = [track_id, name, album, artist, release_date, length, popularity, danceability, acousticness, energy, instrumentalness, liveness, loudness, speechiness, tempo, time_signature, genres]
  return track


for x in spotify_playlist_ids[:200]:
    getTrackIDs(x)
# ids[:5]


# loop over track ids to get audio features for each track
tracks = []
for i in range(len(ids)):
    try:
        print(ids[i])  
        track = getTrackFeatures(ids[i])
        tracks.append(track)
    except:
        continue

# create dataset
df = pd.DataFrame(tracks, columns = ['track_id', 'name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature', 'genres'])
df.to_csv("song_data.csv")

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id, limit = 100)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

results = get_playlist_tracks("Meliodas", "https://open.spotify.com/playlist/7lMeQW9qfnRn13H7xojaBs?si=9318b46daa774c01")

# results = sp.current_user_saved_tracks(limit=50)
liked_songs = []
# for item in results:
#     print(item)
#     print("\n")
for item in results:
    track = getTrackFeatures(item['track']['id'])
    liked_songs.append(track)

df_fav = pd.DataFrame(liked_songs, columns = ['track_id', 'name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature', 'genres'])
df_fav["favorite"] = 1
df["favorite"] = 0

frames = [df, df_fav]
data = pd.concat(frames)

data.to_csv("comb_data2.csv")
