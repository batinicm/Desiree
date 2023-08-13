def extract_info_for_homeview(track):
    extracted_track = track['track']
    image_href = [image['url'] for image in extracted_track['album']['images']][0]
    artist = [artist['name'] for artist in extracted_track['artists']][0]
    return {
        'ImageHref': image_href,
        'Name': extracted_track['name'],
        'Artist': artist
    }
