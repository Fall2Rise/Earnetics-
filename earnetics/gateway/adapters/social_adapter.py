"""
Social Media Adapter: Posts to social platforms (Reddit, Twitter/X, etc.)
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.gateway.adapters.base_adapter import BaseAdapter


class SocialAdapter(BaseAdapter):
    """Adapter for posting to social media platforms"""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        super().__init__(config, credential_vault)
        self.platforms = config.get("social_platforms", {})
    
    def execute(self, action: str, params: Dict[str, Any], 
               agent_id: str, role: str) -> Dict[str, Any]:
        """
        Execute social post action
        
        Params:
            platform: str - "reddit" | "twitter" | "x"
            content: str - Post content
            media_refs: Optional[List[str]] - Media file references
            subreddit: Optional[str] - For Reddit posts
            title: Optional[str] - For Reddit posts
        """
        if action != "social.post":
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Unsupported action: {action}"
            }
        
        platform = params.get("platform", "").lower()
        content = params.get("content", "")
        media_refs = params.get("media_refs", [])
        
        if not platform or not content:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": "Platform and content are required"
            }
        
        try:
            if platform in ["reddit", "oauth.reddit"]:
                return self._post_to_reddit(params)
            elif platform in ["twitter", "x", "api.twitter.com"]:
                return self._post_to_twitter(params)
            else:
                return {
                    "success": False,
                    "data": None,
                    "metadata": {},
                    "citation": {},
                    "error": f"Unsupported platform: {platform}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Social post error: {str(e)}"
            }
    
    def _post_to_reddit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Post to Reddit"""
        import requests
        
        client_id = self.credential_vault.get_secret("reddit_client_id") if self.credential_vault else os.getenv("REDDIT_CLIENT_ID")
        client_secret = self.credential_vault.get_secret("reddit_client_secret") if self.credential_vault else os.getenv("REDDIT_CLIENT_SECRET")
        username = self.credential_vault.get_secret("reddit_username") if self.credential_vault else os.getenv("REDDIT_USERNAME")
        password = self.credential_vault.get_secret("reddit_password") if self.credential_vault else os.getenv("REDDIT_PASSWORD")
        
        if not all([client_id, client_secret, username, password]):
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": "Reddit credentials not configured"
            }
        
        # Get OAuth token
        auth_response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(client_id, client_secret),
            data={
                "grant_type": "password",
                "username": username,
                "password": password
            },
            headers={"User-Agent": "Earnetics/1.0"},
            timeout=10
        )
        
        if auth_response.status_code != 200:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Reddit auth failed: {auth_response.status_code}"
            }
        
        access_token = auth_response.json().get("access_token")
        subreddit = params.get("subreddit", "test")
        title = params.get("title", params.get("content", "")[:100])
        content = params.get("content", "")
        
        # Post to Reddit
        post_response = requests.post(
            f"https://oauth.reddit.com/r/{subreddit}/submit",
            headers={
                "Authorization": f"bearer {access_token}",
                "User-Agent": "Earnetics/1.0"
            },
            data={
                "kind": "self",
                "sr": subreddit,
                "title": title,
                "text": content
            },
            timeout=10
        )
        
        if post_response.status_code in [200, 201]:
            result = post_response.json()
            post_id = result.get("json", {}).get("data", {}).get("id", "")
            return {
                "success": True,
                "data": {
                    "post_id": post_id,
                    "platform": "reddit",
                    "subreddit": subreddit,
                    "url": f"https://reddit.com/r/{subreddit}/comments/{post_id}"
                },
                "metadata": {
                    "platform": "reddit",
                    "posted_at": datetime.utcnow().isoformat()
                },
                "citation": self.create_citation(f"reddit://r/{subreddit}", datetime.utcnow().isoformat())
            }
        else:
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": f"Reddit post failed: {post_response.status_code} - {post_response.text}"
            }
    
    def _post_to_twitter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Post to Twitter/X"""
        # Twitter API v2 requires OAuth 2.0
        # For MVP, return stub response
        # Full implementation would use tweepy or requests_oauthlib
        
        api_key = self.credential_vault.get_secret("twitter_api_key") if self.credential_vault else os.getenv("TWITTER_API_KEY")
        api_secret = self.credential_vault.get_secret("twitter_api_secret") if self.credential_vault else os.getenv("TWITTER_API_SECRET")
        access_token = self.credential_vault.get_secret("twitter_access_token") if self.credential_vault else os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = self.credential_vault.get_secret("twitter_access_secret") if self.credential_vault else os.getenv("TWITTER_ACCESS_SECRET")
        
        if not all([api_key, api_secret, access_token, access_secret]):
            return {
                "success": False,
                "data": None,
                "metadata": {},
                "citation": {},
                "error": "Twitter credentials not configured"
            }
        
        # Stub implementation - full OAuth 1.0a would go here
        # For now, return success with note that it's a stub
        content = params.get("content", "")
        
        return {
            "success": True,
            "data": {
                "post_id": f"stub_{datetime.utcnow().timestamp()}",
                "platform": "twitter",
                "note": "Stub implementation - configure OAuth 1.0a for full functionality"
            },
            "metadata": {
                "platform": "twitter",
                "posted_at": datetime.utcnow().isoformat(),
                "stub": True
            },
            "citation": self.create_citation("twitter://api.twitter.com", datetime.utcnow().isoformat())
        }
