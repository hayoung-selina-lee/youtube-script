import yt_dlp
import xml.etree.ElementTree as ET
import requests
import logging

logger = logging.getLogger(__name__)

def get_subtitles(youtube_url: str):
    logging.info(f"+ get subtitles {youtube_url}")
    try:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
            'writeinfojson': True,
            'outtmpl': '/tmp/%(id)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
        
        tracks = info.get('subtitles', {}).get('en', [])
        if not tracks:
            print('No English captions available for this video.')
            return None
        
        # Assuming that there is a single subtitle file
        subtitle_url = tracks[0]['url']
        response = requests.get(subtitle_url)
        subtitles_xml = response.text
        
        # Parse XML
        root = ET.fromstring(subtitles_xml)
        subtitles = []
        
        for body in root.findall('.//body'):
            for p in body.findall('p'):
                start = p.attrib.get('t')
                dur = p.attrib.get('d')
                text = p.text
                if start and dur and text:
                    subtitles.append({
                        'start': start,
                        'dur': dur,
                        'text': text
                    })
                    subtitles.append(" / ")
        logging.info(f"get subtitles :: SUCCESS +")
        return subtitles.rstrip(" / ")
    
    except Exception as e:
        logging.info(f"get subtitles :: FAIL+")
        print(f'Error getting subtitles: {e}')
        return None
