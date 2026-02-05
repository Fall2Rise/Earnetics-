"""
Website Growth & Digital Presence Service
Manages websites, content, SEO, social integration, and affiliate links
"""
import sqlite3
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class WebsiteGrowthService:
    """Service for managing website growth, content, and digital presence"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self._ensure_tables()
        self.websites = {
            "fallat.digital": {
                "domain": "fallat.digital",
                "url": os.getenv("SITE_BASE_URL", "https://www.fallat.digital"),
                "status": "active",
                "purpose": "Main corporate website and product showcase"
            },
            "earnetics.live": {
                "domain": "earnetics.live",
                "url": os.getenv("SECONDARY_SITE_URL", "https://www.earnetics.live"),
                "status": "active",
                "purpose": "AI corporation operations and revenue platform"
            }
        }
    
    def _ensure_tables(self):
        """Create database tables for website management"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Websites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS managed_websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL UNIQUE,
                    url TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    purpose TEXT,
                    social_accounts TEXT,  -- JSON array of connected social accounts
                    analytics_id TEXT,
                    seo_score INTEGER DEFAULT 0,
                    traffic_monthly INTEGER DEFAULT 0,
                    last_updated TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Blog posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    author TEXT,
                    category TEXT,
                    tags TEXT,  -- JSON array
                    seo_keywords TEXT,  -- JSON array
                    affiliate_links TEXT,  -- JSON array of affiliate links
                    status TEXT DEFAULT 'draft',  -- draft, published, scheduled
                    published_at TEXT,
                    views INTEGER DEFAULT 0,
                    engagement_score REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (website_id) REFERENCES managed_websites(id)
                )
            """)
            
            # Social media connections
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS social_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    platform TEXT NOT NULL,  -- twitter, linkedin, facebook, etc.
                    account_handle TEXT NOT NULL,
                    access_token TEXT,
                    status TEXT DEFAULT 'connected',
                    last_sync TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (website_id) REFERENCES managed_websites(id)
                )
            """)
            
            # Affiliate links
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    blog_post_id INTEGER,
                    product_id INTEGER,
                    affiliate_program TEXT,  -- amazon, clickbank, etc.
                    link_url TEXT NOT NULL,
                    link_text TEXT,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (website_id) REFERENCES managed_websites(id),
                    FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id)
                )
            """)
            
            # Website analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS website_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    date TEXT NOT NULL,
                    page_views INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    bounce_rate REAL DEFAULT 0.0,
                    avg_session_duration REAL DEFAULT 0.0,
                    top_pages TEXT,  -- JSON array
                    traffic_sources TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (website_id) REFERENCES managed_websites(id),
                    UNIQUE(website_id, date)
                )
            """)
            
            conn.commit()
            
            # Initialize default websites
            self._initialize_websites()
    
    def _initialize_websites(self):
        """Initialize default websites if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for domain, info in self.websites.items():
                cursor.execute("""
                    INSERT OR IGNORE INTO managed_websites 
                    (domain, url, status, purpose, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    info["domain"],
                    info["url"],
                    info["status"],
                    info["purpose"],
                    datetime.now(timezone.utc).isoformat()
                ))
            conn.commit()
    
    def get_websites(self) -> List[Dict[str, Any]]:
        """Get all managed websites"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM managed_websites ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_website(self, domain: str, url: str, purpose: str = "") -> Dict:
        """Add a new website to manage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO managed_websites (domain, url, purpose, created_at)
                    VALUES (?, ?, ?, ?)
                """, (domain, url, purpose, datetime.now(timezone.utc).isoformat()))
                conn.commit()
                return {"success": True, "message": f"Website {domain} added"}
            except sqlite3.IntegrityError:
                return {"success": False, "message": f"Website {domain} already exists"}
    
    def create_blog_post(
        self,
        website_id: int,
        title: str,
        content: str,
        author: str = "AI Content Writer",
        category: str = "General",
        tags: List[str] = None,
        seo_keywords: List[str] = None,
        affiliate_links: List[Dict[str, str]] = None
    ) -> Dict:
        """Create a new blog post"""
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO blog_posts 
                (website_id, title, content, slug, author, category, tags, seo_keywords, affiliate_links, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                website_id,
                title,
                content,
                slug,
                author,
                category,
                json.dumps(tags or []),
                json.dumps(seo_keywords or []),
                json.dumps(affiliate_links or []),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            post_id = cursor.lastrowid
            
            # Add affiliate links if provided
            if affiliate_links:
                for link in affiliate_links:
                    cursor.execute("""
                        INSERT INTO affiliate_links 
                        (website_id, blog_post_id, affiliate_program, link_url, link_text, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        website_id,
                        post_id,
                        link.get("program", "unknown"),
                        link.get("url", ""),
                        link.get("text", ""),
                        datetime.now(timezone.utc).isoformat()
                    ))
            
            conn.commit()
            return {"success": True, "post_id": post_id, "slug": slug}
    
    def publish_blog_post(self, post_id: int) -> Dict:
        """Publish a blog post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE blog_posts
                SET status = 'published',
                    published_at = ?,
                    updated_at = ?
                WHERE id = ?
            """, (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), post_id))
            conn.commit()
            return {"success": True, "message": "Blog post published"}
    
    def get_blog_posts(self, website_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get blog posts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM blog_posts WHERE 1=1"
            params = []
            
            if website_id:
                query += " AND website_id = ?"
                params.append(website_id)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                post = dict(row)
                post["tags"] = json.loads(post.get("tags") or "[]")
                post["seo_keywords"] = json.loads(post.get("seo_keywords") or "[]")
                post["affiliate_links"] = json.loads(post.get("affiliate_links") or "[]")
                posts.append(post)
            
            return posts
    
    def connect_social_account(
        self,
        website_id: int,
        platform: str,
        account_handle: str,
        access_token: Optional[str] = None
    ) -> Dict:
        """Connect a social media account to a website"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO social_connections
                (website_id, platform, account_handle, access_token, status, created_at)
                VALUES (?, ?, ?, ?, 'connected', ?)
            """, (website_id, platform, account_handle, access_token, datetime.now(timezone.utc).isoformat()))
            conn.commit()
            return {"success": True, "message": f"Connected {platform} account"}
    
    def get_social_connections(self, website_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get social media connections"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if website_id:
                cursor.execute("SELECT * FROM social_connections WHERE website_id = ?", (website_id,))
            else:
                cursor.execute("SELECT * FROM social_connections")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_affiliate_link(
        self,
        website_id: int,
        blog_post_id: Optional[int],
        product_id: Optional[int],
        affiliate_program: str,
        link_url: str,
        link_text: str = ""
    ) -> Dict:
        """Add an affiliate link"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO affiliate_links
                (website_id, blog_post_id, product_id, affiliate_program, link_url, link_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                website_id,
                blog_post_id,
                product_id,
                affiliate_program,
                link_url,
                link_text,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "link_id": cursor.lastrowid}
    
    def get_affiliate_links(self, website_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get affiliate links"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if website_id:
                cursor.execute("SELECT * FROM affiliate_links WHERE website_id = ?", (website_id,))
            else:
                cursor.execute("SELECT * FROM affiliate_links")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_analytics(
        self,
        website_id: int,
        page_views: int = 0,
        unique_visitors: int = 0,
        bounce_rate: float = 0.0,
        avg_session_duration: float = 0.0,
        top_pages: List[str] = None,
        traffic_sources: Dict[str, Any] = None
    ) -> Dict:
        """Update website analytics"""
        today = datetime.now(timezone.utc).date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO website_analytics
                (website_id, date, page_views, unique_visitors, bounce_rate, avg_session_duration, top_pages, traffic_sources, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                website_id,
                today,
                page_views,
                unique_visitors,
                bounce_rate,
                avg_session_duration,
                json.dumps(top_pages or []),
                json.dumps(traffic_sources or {}),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True}
    
    def get_analytics(self, website_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get website analytics for the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM website_analytics
                WHERE website_id = ? AND date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (website_id, days))
            
            rows = cursor.fetchall()
            analytics = []
            for row in rows:
                data = dict(row)
                data["top_pages"] = json.loads(data.get("top_pages") or "[]")
                data["traffic_sources"] = json.loads(data.get("traffic_sources") or "{}")
                analytics.append(data)
            
            return analytics
