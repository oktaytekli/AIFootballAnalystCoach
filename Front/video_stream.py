import yt_dlp

def get_direct_url(youtube_url):
    """
    Resolves the YouTube URL to a direct stream link (HLS/m3u8) 
    compatible with OpenCV to avoid connection drops.
    """
    ydl_opts = {
        'format': 'best[protocol^=m3u8]/best',
        'quiet': True,
        'noplaylist': True,
        'force_generic_extractor': False,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Resolving video stream protocol (HLS): {youtube_url}")
            info = ydl.extract_info(youtube_url, download=False)
            
            if 'url' in info:
                return info['url']
            elif 'entries' in info:
                return info['entries'][0]['url']
            else:
                print("No suitable video format found.")
                return None
                
    except Exception as e:
        print(f"YouTube connection error: {e}")
        return None