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
import sklearn
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

st.set_page_config(
        page_title="Spotify Vibelist",
)

SPOTIPY_CLIENT_ID = "a77d4744434b4f81a84e3c7463402eeb"
SPOTIPY_CLIENT_SECRET = "068628f43c1e413c845cbed1deabaad1"

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id, limit = 100)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def getTrackFeatures(track_id):
  meta = sp.track(track_id)
  features = sp.audio_features(track_id)

  # meta
  name = meta['name']
  track_id = track_id
  album = meta['album']['name']
  artist = meta['album']['artists'][0]['name']
  popularity = meta['popularity']
#   if meta['album']['genres']:
#     genres = meta['album']['genres']
#   else:
#       genres = ""

  # features
  acousticness = features[0]['acousticness']
  danceability = features[0]['danceability']
  energy = features[0]['energy']
  instrumentalness = features[0]['instrumentalness']
  liveness = features[0]['liveness']
  loudness = features[0]['loudness']
  speechiness = features[0]['speechiness']
  tempo = features[0]['tempo']

  track = [name, track_id, album, artist, popularity, danceability, acousticness, energy, instrumentalness, liveness, loudness, speechiness, tempo]
  return track


def recommend_songs(df, vector, play_features):
    temp = pd.DataFrame()
    # Find cosine similarity between the playlist and the complete song set
    play_features['sim'] = cosine_similarity(play_features.drop(['name','track_id', 'album', 'artist'], axis = 1).values, vector.values.reshape(1, -1))[:,0]
    top_songs = play_features.sort_values('sim',ascending = False).head(40)
    
    return top_songs


st.title("Spotify Content-Based Filtering Recommender")
st.header("Hello there! Ready to explore new songs from Spotify?")

st.caption("Step 1: Open your Spotify account in a browser.")

st.caption("Step 2: Find a playlist of your choosing and click on it.")
st.image("step3.jpg")

st.caption("Step 3: Click the 3 dots and select the circled option.")
st.image("step4.jpg")


in_playlist = st.text_input("Enter the copied link below!")

if in_playlist:
    results = get_playlist_tracks("Meliodas", in_playlist)
    general = pd.read_csv("final_data.csv")

    ids = []
    for ele in results:
        ids.append(ele['track']['id'])

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
    df = pd.DataFrame(tracks, columns = ['name','track_id', 'album', 'artist', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo'])

    vector_df = df.drop(['name','track_id', 'album', 'artist'], axis = 1)

    vector_df = vector_df.sum(axis = 0)

    recs = recommend_songs(general, vector_df, df)
    display_recs = recs[['name', 'album', 'artist']].copy()

    st.dataframe(display_recs)

