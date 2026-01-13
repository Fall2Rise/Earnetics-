"""
Community Management Service
Manages Earnetics community - forums, Discord, engagement, growth
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CommunityService:
    """Service for managing Earnetics community"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create database tables for community management"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Community platforms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_platforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_type TEXT NOT NULL,  -- discord, forum, slack, etc.
                    platform_name TEXT NOT NULL,
                    platform_url TEXT,
                    invite_link TEXT,
                    member_count INTEGER DEFAULT 0,
                    active_members INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    api_key TEXT,
                    webhook_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Community members
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    username TEXT,
                    platform_id TEXT,  -- Platform-specific ID
                    platform_type TEXT,  -- discord, forum, etc.
                    join_date TEXT,
                    last_active TEXT,
                    engagement_score REAL DEFAULT 0.0,
                    role TEXT DEFAULT 'member',  -- member, moderator, admin
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL
                )
            """)
            
            # Community posts/discussions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id INTEGER,
                    author_id INTEGER,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    views INTEGER DEFAULT 0,
                    replies INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'published',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (platform_id) REFERENCES community_platforms(id),
                    FOREIGN KEY (author_id) REFERENCES community_members(id)
                )
            """)
            
            # Community events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id INTEGER,
                    event_type TEXT,  -- webinar, meetup, launch, etc.
                    title TEXT NOT NULL,
                    description TEXT,
                    event_date TEXT,
                    registration_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'scheduled',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (platform_id) REFERENCES community_platforms(id)
                )
            """)
            
            conn.commit()
            
            # Initialize default platforms
            self._initialize_platforms()
    
    def _initialize_platforms(self):
        """Initialize default community platforms"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            platforms = [
                {
                    "platform_type": "discord",
                    "platform_name": "Earnetics Community",
                    "platform_url": "https://discord.gg/earnetics",
                    "status": "active"
                },
                {
                    "platform_type": "forum",
                    "platform_name": "Earnetics Forum",
                    "platform_url": "https://www.earnetics.live/community",
                    "status": "active"
                },
            ]
            
            for platform in platforms:
                cursor.execute("""
                    INSERT OR IGNORE INTO community_platforms
                    (platform_type, platform_name, platform_url, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    platform["platform_type"],
                    platform["platform_name"],
                    platform["platform_url"],
                    platform["status"],
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            conn.commit()
    
    def add_platform(self, platform_type: str, platform_name: str, platform_url: str = "", invite_link: str = "") -> Dict:
        """Add a new community platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO community_platforms
                (platform_type, platform_name, platform_url, invite_link, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                platform_type,
                platform_name,
                platform_url,
                invite_link,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "platform_id": cursor.lastrowid}
    
    def get_platforms(self) -> List[Dict[str, Any]]:
        """Get all community platforms"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM community_platforms WHERE status = 'active'")
            return [dict(row) for row in cursor.fetchall()]
    
    def add_member(self, email: str, username: str, platform_type: str, platform_id: str = "") -> Dict:
        """Add a community member"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO community_members
                (email, username, platform_type, platform_id, join_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                email,
                username,
                platform_type,
                platform_id,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "member_id": cursor.lastrowid}
    
    def get_members(self, platform_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get community members"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if platform_type:
                cursor.execute("SELECT * FROM community_members WHERE platform_type = ?", (platform_type,))
            else:
                cursor.execute("SELECT * FROM community_members")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def create_post(self, platform_id: int, author_id: int, title: str, content: str, category: str = "general") -> Dict:
        """Create a community post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO community_posts
                (platform_id, author_id, title, content, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                platform_id,
                author_id,
                title,
                content,
                category,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "post_id": cursor.lastrowid}
    
    def schedule_event(self, platform_id: int, event_type: str, title: str, description: str, event_date: str) -> Dict:
        """Schedule a community event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO community_events
                (platform_id, event_type, title, description, event_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                platform_id,
                event_type,
                title,
                description,
                event_date,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "event_id": cursor.lastrowid}
    
    def update_member_count(self, platform_id: int, member_count: int, active_members: int = 0):
        """Update platform member counts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE community_platforms
                SET member_count = ?, active_members = ?, updated_at = ?
                WHERE id = ?
            """, (member_count, active_members, datetime.now(timezone.utc).isoformat(), platform_id))
            conn.commit()
