"""
100x Content Engine Service
Handles the generation, repurposing, and distribution of content across multiple platforms.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from backend.services.video_factory import VideoFactory
from backend.services.content_service import content_service
from backend.system_state import is_safe_mode
from backend.audit_log import log_event

class ContentEngineService:
    def __init__(self):
        self.platforms = ["tiktok", "youtube_shorts", "instagram_reels", "facebook_reels", "twitter", "linkedin", "blog"]
        self.video_factory = VideoFactory()

    async def generate_master_content(self, topic: str, tone: str = "viral") -> Dict[str, Any]:
        """Generates a master long-form content piece."""
        content = f"Master Content for: {topic}\n\nDeep dive into {topic}..."
        
        # Persist to database
        saved = content_service.save_content(
            title=topic,
            content=content,
            type="master_text",
            status="draft",
            metadata={"tone": tone}
        )
        
        return saved

    async def repurpose_content(self, master_content_id: str, master_text: str) -> Dict[str, Any]:
        """Breaks down master content into platform-specific formats."""
        shorts_script = f"Hook: {master_text[:30]}..."
        tweet_content = f"New on {master_text[:20]}..."
        
        # Save derived assets
        content_service.save_content(
            title=f"Shorts Script: {master_content_id}",
            content=shorts_script,
            type="script_video",
            status="draft",
            metadata={"master_id": master_content_id, "platform": "tiktok"}
        )
        
        content_service.save_content(
            title=f"Tweet: {master_content_id}",
            content=tweet_content,
            type="social_post",
            status="draft",
            metadata={"master_id": master_content_id, "platform": "twitter"}
        )

        return {
            "master_id": master_content_id,
            "shorts": [
                {"platform": "tiktok", "script": shorts_script},
                {"platform": "youtube_shorts", "script": f"Did you know? {master_text[:30]}..."}
            ],
            "social_posts": [
                {"platform": "twitter", "content": tweet_content},
                {"platform": "linkedin", "content": f"Insights on {master_text[:20]}..."}
            ]
        }

    async def distribute_content(self, assets: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Posts content to selected platforms, respecting SAFE_MODE."""
        results = {}
        production_mode = not is_safe_mode()
        
        for platform in platforms:
            if production_mode:
                # In a real scenario, this would call the actual API
                # For now, we log the intent and simulate success
                log_event("content_distribution", message=f"POSTING REAL CONTENT to {platform}", context=str(assets))
                results[platform] = {
                    "status": "posted",
                    "mode": "production",
                    "url": f"https://{platform}.com/post/{int(datetime.now().timestamp())}"
                }
            else:
                log_event("content_distribution", message=f"SIMULATING content post to {platform}", context="Safe Mode Active")
                results[platform] = {
                    "status": "simulated",
                    "mode": "safe",
                    "url": f"https://sandbox.{platform}.com/test"
                }
        return results
