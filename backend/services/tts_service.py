"""
Text-to-Speech service for Atom voice responses.
Uses Windows native Edge TTS for high-quality voice synthesis.
"""

import logging
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Audio cache directory
AUDIO_CACHE_DIR = Path(__file__).parent.parent.parent / "static" / "audio" / "atom"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Voice settings - Professional male voice for Atom
VOICE_NAME = "en-US-ChristopherNeural"  # Professional male voice
FALLBACK_VOICE = "en-US-GuyNeural"  # Alternative male voice
SPEECH_RATE = "+0%"  # Normal speed
SPEECH_PITCH = "+0Hz"  # Normal pitch

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class TTSService:
    """Text-to-Speech service for generating Atom voice responses."""
    
    def __init__(self):
        self.voice_name = VOICE_NAME
        self.cache_dir = AUDIO_CACHE_DIR
        self.use_cache = True
        if EDGE_TTS_AVAILABLE:
            logger.info("✅ Edge TTS available - using Windows native TTS for Atom voice")
        elif PYTTSX3_AVAILABLE:
            logger.info("✅ pyttsx3 available - using as TTS fallback for Atom voice")
        else:
            logger.warning("⚠️ No TTS engine available - install with: pip install edge-tts")
        
    async def generate_speech(self, text: str) -> Optional[Dict[str, str]]:
        """
        Generate speech audio from text.
        Returns dict with 'audio_url' and 'audio_path' or None if failed.
        """
        if not text or not text.strip():
            return None
            
        # Clean text for filename
        text_hash = str(hash(text))[:12]
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"atom_{timestamp}_{text_hash}.mp3"
        audio_path = self.cache_dir / filename
        
        # Check cache first
        if self.use_cache and audio_path.exists():
            logger.debug(f"Using cached audio: {filename}")
            return {
                "audio_url": f"/static/audio/atom/{filename}",
                "audio_path": str(audio_path),
                "cached": True
            }
        
        # Generate new audio
        try:
            if EDGE_TTS_AVAILABLE:
                return await self._generate_with_edge_tts(text, audio_path)
            elif PYTTSX3_AVAILABLE:
                return await self._generate_with_pyttsx3(text, audio_path)
            else:
                logger.warning("No TTS engine available")
                return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    async def _generate_with_edge_tts(self, text: str, output_path: Path) -> Optional[Dict[str, str]]:
        """Generate speech using Edge TTS (Windows native)."""
        try:
            # Try preferred voice first
            voice = self.voice_name
            try:
                communicate = edge_tts.Communicate(text=text, voice=voice, rate=SPEECH_RATE, pitch=SPEECH_PITCH)
                await communicate.save(str(output_path))
            except Exception as e:
                logger.warning(f"Failed with voice {voice}, trying fallback: {e}")
                voice = FALLBACK_VOICE
                communicate = edge_tts.Communicate(text=text, voice=voice, rate=SPEECH_RATE, pitch=SPEECH_PITCH)
                await communicate.save(str(output_path))
            
            logger.info(f"✅ Generated TTS audio: {output_path.name}")
            return {
                "audio_url": f"/static/audio/atom/{output_path.name}",
                "audio_path": str(output_path),
                "cached": False,
                "voice": voice
            }
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}")
            return None
    
    def _generate_with_pyttsx3(self, text: str, output_path: Path) -> Optional[Dict[str, str]]:
        """Generate speech using pyttsx3 (fallback)."""
        try:
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            # Prefer male voice
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            # Save to file
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
            logger.info(f"✅ Generated TTS audio (pyttsx3): {output_path.name}")
            return {
                "audio_url": f"/static/audio/atom/{output_path.name}",
                "audio_path": str(output_path),
                "cached": False,
                "engine": "pyttsx3"
            }
        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            return None
    
    async def list_voices(self) -> list:
        """List available TTS voices."""
        if EDGE_TTS_AVAILABLE:
            try:
                voices = await edge_tts.list_voices()
                return [v for v in voices if v['Locale'].startswith('en-')]
            except Exception:
                return []
        return []

# Global TTS service instance
tts_service = TTSService()

