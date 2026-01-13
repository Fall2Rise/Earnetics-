"""
Local Video Factory
Generates actual .mp4 video files locally using MoviePy and gTTS.
No external paid APIs required.
"""
import os
import textwrap

try:
    from gtts import gTTS
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    # Create dummy classes for type hints
    ColorClip = None
    TextClip = None
    CompositeVideoClip = None
    AudioFileClip = None

class VideoFactory:
    def __init__(self, output_dir="static/generated_videos"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_video(self, text: str, filename: str = "output.mp4") -> str:
        """
        Generates a simple text-on-background video with voiceover.
        Returns the path to the generated video file.
        """
        try:
            # 1. Generate Audio (Voiceover)
            audio_path = os.path.join(self.output_dir, "temp_audio.mp3")
            tts = gTTS(text=text, lang='en')
            tts.save(audio_path)
            
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 1.0 # Add 1s padding
            
            # 2. Create Background (Dark Blue)
            # Size: 1080x1920 (Vertical Short format)
            bg_clip = ColorClip(size=(1080, 1920), color=(10, 20, 40), duration=duration)
            
            # 3. Create Text Overlay
            # Wrap text to fit screen
            wrapped_text = "\n".join(textwrap.wrap(text, width=30))
            
            # Note: TextClip requires ImageMagick. If not installed, this might fail.
            # We use a default font.
            try:
                txt_clip = TextClip(wrapped_text, fontsize=70, color='white', font='Arial', size=(900, 1600), method='caption')
                txt_clip = txt_clip.set_pos('center').set_duration(duration)
                video = CompositeVideoClip([bg_clip, txt_clip])
            except Exception as e:
                print(f"Warning: TextClip failed (ImageMagick missing?). Generating audio-only video. Error: {e}")
                video = bg_clip # Fallback to just background
            
            # 4. Combine and Export
            video = video.set_audio(audio_clip)
            output_path = os.path.join(self.output_dir, filename)
            
            # Write file (using 'libx264' codec for compatibility)
            video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            
            # Cleanup temp audio
            audio_clip.close()
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
            return output_path

        except Exception as e:
            print(f"❌ Video Generation Failed: {e}")
            return ""

if __name__ == "__main__":
    # Test
    factory = VideoFactory()
    path = factory.generate_video("This is a test of the Local Video Factory. It creates videos for free!", "test_video.mp4")
    print(f"Generated: {path}")
