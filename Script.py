import os
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
import argparse
import sys

def validate_youtube_url(url):
    """Validate if the URL is a proper YouTube URL."""
    try:
        parsed = urlparse(url)
        if parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']:
            if 'v=' in parsed.query:
                video_id = parse_qs(parsed.query)['v'][0]
                return True
            elif parsed.path.startswith('/watch'):
                return True
            elif parsed.netloc == 'youtu.be':
                return True
        return False
    except:
        return False

def get_video_info(yt):
    """Get video information."""
    print("\nVideo Information:")
    print(f"Title: {yt.title}")
    print(f"Author: {yt.author}")
    print(f"Length: {yt.length} seconds")
    print(f"Views: {yt.views:,}")
    print(f"Rating: {yt.rating}")

def download_video(url, output_path='./downloads', quality='highest', audio_only=False):
    """Download YouTube video."""
    try:
        yt = YouTube(url)
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        get_video_info(yt)
        
        if audio_only:
            print("\nDownloading audio...")
            stream = yt.streams.get_audio_only()
        else:
            print("\nDownloading video...")
            if quality == 'highest':
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(res=quality, progressive=True).first()
                if not stream:
                    print(f"No stream found with quality {quality}. Downloading highest quality instead.")
                    stream = yt.streams.get_highest_resolution()
        
        print(f"Downloading: {yt.title} ({stream.resolution if not audio_only else 'audio'})...")
        stream.download(output_path)
        print("\nDownload completed successfully!")
        print(f"File saved to: {os.path.join(output_path, yt.title)}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

def interactive_mode():
    """Run the script in interactive mode."""
    print("YouTube Video Downloader")
    print("-----------------------")
    
    while True:
        url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()
        if url.lower() == 'q':
            break
            
        if not validate_youtube_url(url):
            print("Invalid YouTube URL. Please try again.")
            continue
            
        print("\nDownload options:")
        print("1. Highest quality video")
        print("2. Specific quality")
        print("3. Audio only")
        choice = input("Enter your choice (1-3): ").strip()
        
        output_path = input(f"Enter output directory (leave blank for './downloads'): ").strip()
        output_path = output_path if output_path else './downloads'
        
        if choice == '1':
            download_video(url, output_path)
        elif choice == '2':
            quality = input("Enter quality (e.g., 720p, 1080p): ").strip()
            download_video(url, output_path, quality)
        elif choice == '3':
            download_video(url, output_path, audio_only=True)
        else:
            print("Invalid choice. Downloading highest quality by default.")
            download_video(url, output_path)

def main():
    parser = argparse.ArgumentParser(description='YouTube Video Downloader')
    parser.add_argument('url', nargs='?', help='YouTube video URL')
    parser.add_argument('-o', '--output', help='Output directory', default='./downloads')
    parser.add_argument('-q', '--quality', help='Video quality (e.g., 720p, 1080p)', default='highest')
    parser.add_argument('-a', '--audio', help='Download audio only', action='store_true')
    
    args = parser.parse_args()
    
    if args.url:
        if not validate_youtube_url(args.url):
            print("Error: Invalid YouTube URL")
            sys.exit(1)
        download_video(args.url, args.output, args.quality, args.audio)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
