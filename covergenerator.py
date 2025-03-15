import io
from spotipy import Spotify
from PIL import Image
import requests
from io import BytesIO

def get_album_cover(access_token):
    
    sp = Spotify(auth=access_token)
    results = sp.current_user_top_tracks(limit=50, time_range='long_term')
    top_tracks = results['items']

    album_covers = []
    for track in top_tracks:
        album_cover_url = track['album']['images'][0]['url']
        response = requests.get(album_cover_url)
        img = Image.open(BytesIO(response.content))
        album_covers.append(img)

    collage = create_7x7_pixelated_collage(album_covers)

    # Convert the image to bytes for displaying in Streamlit
    img_bytes = io.BytesIO()
    collage.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def create_7x7_pixelated_collage(images, grid_size=(7, 7), output_size=700):
    rows, cols = grid_size
    tile_size = output_size // rows  # Size of each tile in the collage
    collage = Image.new('RGB', (output_size, output_size), "white")

    for row in range(rows):
        for col in range(cols):
            # Calculate the position for the current tile in the collage
            collage_x = col * tile_size
            collage_y = row * tile_size

            # Loop through the images and extract the corresponding tile
            img_idx = (row * cols + col) % len(images)  # Cycle through images
            img = images[img_idx]

            # Resize the image to match the grid size
            img_resized = img.resize((output_size, output_size))

            # Calculate the crop region for the tile
            tile_x = col * tile_size
            tile_y = row * tile_size
            tile = img_resized.crop((tile_x, tile_y, tile_x + tile_size, tile_y + tile_size))

            # Paste the tile into the collage
            collage.paste(tile, (collage_x, collage_y))

    return collage