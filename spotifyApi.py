import base64
import requests
import six
import json
import time
import collections

CLIENT_ID = 'idhere'
CLIENT_SECRET = 'secrethere'

class SpotifyOauthError(Exception):
    pass

class SpotifyAPI:


    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()
        with open('db.json') as infile:
            self.db = json.load(infile)

    def compare_genre_profiles(self, gp1, gp2):
        gp1 = dict(gp1)
        gp2 = dict(gp2)

        for key in gp1:
            if key not in gp2:
                gp2[key] = 0


        for key in gp2:
            if key not in gp1:
                gp1[key] = 0

        sum_of_squared_distances = 0
        for key in gp1:
            if key in gp2:
                difference = abs(gp1[key] - gp2[key])
                sum_of_squared_distances += (difference * difference)

        return sum_of_squared_distances * 2.5

    def _make_authoriztion_headers(self):
        # no idea what six does... copied from spotipy
        auth_header = base64.b64encode(six.text_type(self.client_id + ':' + self.client_secret).encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

    def get_access_token(self):
        payload = {'grant_type': 'client_credentials'}
        headers = self._make_authoriztion_headers()
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload,
                                 verify=True)
        if response.status_code != 200:
            raise SpotifyOauthError(response.reason)

        token_info = response.json()
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        return token_info['access_token']

    def get_user_playlists(self, user_id):
        auth_header = {"Authorization": "Bearer {}".format(self.access_token)}
        response = requests.get('https://api.spotify.com/v1/users/{}/playlists'.format(user_id), headers=auth_header)
        user_response = requests.get('https://api.spotify.com/v1/users/{}'.format(user_id), headers=auth_header).json()
        name = user_response['display_name']

        return response.json(), name

    def get_playlist_artists(self, tracks_href):
        auth_header = {"Authorization": "Bearer {}".format(self.access_token)}
        response = requests.get(tracks_href, headers=auth_header).json()
        artist_hrefs = []

        for track in response['items']:
            if track != None and track['track'] != None:
                artists = track['track']['artists']
                for artist in artists:
                    artist_hrefs.append(artist['href'])



        return artist_hrefs

    def get_all_artist_genres(self, artist_hrefs):
        auth_header = {"Authorization": "Bearer {}".format(self.access_token)}
        artist_segments = []
        new = []


        for href in artist_hrefs:
            flag = True
            for entry in self.db:

                if entry['href'] == href:
                    flag = False
                    break

            if flag:
                if len(new) < 50:
                    new.append(href)
                else:
                    artist_segments.append(new)
                    new = [href]
        if len(new) > 0:
            artist_segments.append(new)



        for segment in artist_segments:
            qstr = 'https://api.spotify.com/v1/artists?ids='
            for href in segment:
                if href != None:
                    id = href.split('/')[-1]
                    qstr = qstr + id + ','
            qstr = qstr[:-1]
            if qstr == 'https://api.spotify.com/v1/artists?ids':
                break
            response = requests.get(qstr, headers=auth_header).json()
            artists = response['artists']
            for artist in artists:
                artist_data = {
                    'genres': artist['genres'],
                    'href':  artist['href'],
                    '_id': artist['id'],
                    'name': artist['name'],
                    'popularity': artist['popularity']
                }

                self.db.append(artist_data)






    def get_artist_genres(self, artist_href):
        flag = True
        for entry in self.db:
            if entry['href'] == artist_href:
                artist_data = entry
                flag = False

        else:
            return artist_data['genres']

    def get_genre_profile(self, user_id):
        response, name = self.get_user_playlists(user_id)
        tracks_hrefs = []

        for playlist in response['items']:

            tracks_hrefs.append(playlist['tracks']['href'])


        artist_hrefs = []
        for tracks in tracks_hrefs:
            artist_hrefs.extend(self.get_playlist_artists(tracks))


        self.get_all_artist_genres(artist_hrefs)

        artist_count = collections.Counter(artist_hrefs)
        keys = tuple(artist_count.keys())
        values = tuple(artist_count.values())




        genre_count = {}

        for i in range(len(keys)):
            if keys[i] == None:
                continue

            genres = self.get_artist_genres(keys[i])
            if genres != None:
                for genre in genres:
                    if genre not in genre_count:
                        genre_count[genre] = values[i]
                    else:
                        genre_count[genre] += values[i]

        total = 0
        for key in genre_count:
            total += genre_count[key]
        for key in genre_count:
            genre_count[key] /= total

        sorted_genre_count = sorted(genre_count.items(), key=lambda kv: kv[1], reverse=True)
        genre_count = collections.OrderedDict(sorted_genre_count)
        with open('db.json', 'w') as outfile:
            json.dump(self.db, outfile)

        return sorted_genre_count, name
