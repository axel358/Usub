import urllib.parse as urlparse

def get_video_id(url):
    url_data = urlparse.urlparse(url)
    if url_data.hostname == 'youtu.be':
        return url_data.path[1:]
    if url_data.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if url_data.path == '/watch':
            query = urlparse.parse_qs(url_data.query)
            return query['v'][0]
        if url_data.path[:7] == '/embed/':
            return url_data.path.split('/')[2]
        if url_data.path[:3] == '/v/':
            return url_data.path.split('/')[2]
    return None
