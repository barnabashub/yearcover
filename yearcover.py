import base64
import requests
import streamlit as st
import covergenerator

spotify_accounts_endpoint = "https://accounts.spotify.com/"
spotify_api_endpoint = "https://api.spotify.com/v1/"

# Variable setup
code_str = "code"
scopes = "user-read-private user-read-email playlist-read-private user-follow-read user-top-read user-read-recently-played user-library-read"
client_id_str = "client_id"
client_secret_str = "client_secret"
redirect_uri_str = "redirect_uri"

# Where the real magic starts. Retrieves an access token and runs the rest of the app.
def login(initial_oauth_token, client_id, client_secret, redirect_uri):
    # Set up for the API call to retrieve an access token
    base64_encoding = "ascii"

    # Headers with Base64 auth encoding
    get_bearer_token_headers = {
        "Authorization": "Basic "
        + base64.b64encode(
            f"{client_id}:{client_secret}".encode(base64_encoding)
        ).decode(base64_encoding),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Payload
    get_bearer_token_payload = {
        "grant_type": "authorization_code",
        "code": initial_oauth_token,
        "redirect_uri": redirect_uri,
    }

    # HTTP POST
    get_bearer_token_response = requests.post(
        f"{spotify_accounts_endpoint}api/token",
        headers=get_bearer_token_headers,
        data=get_bearer_token_payload,
    )

    # Crash on error (no automated data pipelines to disrupt here...)
    get_bearer_token_response.raise_for_status()

    # Read the resulting JSON and retrieve your access token!
    get_bearer_token_response_json = get_bearer_token_response.json()
    access_token = get_bearer_token_response_json["access_token"]

    # Placeholder for the rest of the app logic
    app_logic(access_token)


def connect():
    # Read from local secrets (when locally run) file or app secrets (when running deployed version).
    client_id = st.secrets[client_id_str]
    client_secret = st.secrets[client_secret_str]
    redirect_uri = st.secrets[redirect_uri_str]

    # Get the query parameters of the URL in the browser
    query_params = st.query_params

    # If there is no OAuth 2.0 code in the query parameters, generate the Welcome screen.
    if code_str not in query_params:
        oath_token_url = f"{spotify_accounts_endpoint}authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"

        st.title("Welcome to YearCover!")
        st.link_button("Log in", oath_token_url)

    # If there is an OAuth 2.0 code in the query parameters, run the analysis.
    else:
        # Grab your token
        oauth_initial_token = query_params[code_str]

        # Removes the query parameters from the browser URL and does not rerun the page
        st.query_params.clear()

        # Set the default layout for the frontend
        st.set_page_config(layout="wide")

        # Run the analysis.
        login(oauth_initial_token, client_id, client_secret, redirect_uri)


def app_logic(access_token):
    st.title("YearCover")
    st.write("Here is your YearCover! This is a collage of your top 50 tracks from Spotify.")
    with st.spinner("Generating the image... Please wait."):
        collage = covergenerator.get_album_cover(access_token)
    st.image(collage)
    

if __name__ == "__main__":
    connect()