"""
Credential Suggestions Service
Dynamically suggests credentials needed based on revenue opportunities and agent discoveries
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CredentialSuggestionsService:
    """Service for managing suggested credentials based on revenue opportunities"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self._ensure_tables()
        self._initialize_default_suggestions()
    
    def _ensure_tables(self):
        """Create database tables for credential suggestions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Suggested credentials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credential_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    revenue_impact TEXT,  -- high, medium, low
                    revenue_stream TEXT,  -- Which revenue stream this enables
                    priority INTEGER DEFAULT 5,  -- 1-10, higher = more important
                    status TEXT DEFAULT 'suggested',  -- suggested, added, dismissed
                    discovered_by TEXT,  -- Which agent/department discovered this
                    discovered_at TEXT,
                    metadata TEXT,  -- JSON for additional info
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(service, name)
                )
            """)
            
            # Revenue stream to credential mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_credential_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    revenue_stream TEXT NOT NULL,
                    required_credentials TEXT,  -- JSON array of {service, name}
                    discovered_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _initialize_default_suggestions(self):
        """Initialize default credential suggestions for common revenue streams"""
        default_suggestions = [
            {
                "service": "stripe",
                "name": "SECRET_KEY",
                "description": "Stripe secret key for payment processing - enables product sales and revenue collection",
                "revenue_impact": "high",
                "revenue_stream": "Product Sales",
                "priority": 10,
                "discovered_by": "System",
            },
            {
                "service": "stripe",
                "name": "PUBLISHABLE_KEY",
                "description": "Stripe publishable key for frontend payment forms",
                "revenue_impact": "high",
                "revenue_stream": "Product Sales",
                "priority": 9,
                "discovered_by": "System",
            },
            {
                "service": "smtp",
                "name": "EMAIL_CREDENTIALS",
                "description": "SMTP credentials for email marketing campaigns - enables lead nurturing and sales",
                "revenue_impact": "high",
                "revenue_stream": "Email Marketing",
                "priority": 9,
                "discovered_by": "System",
            },
            {
                "service": "paypal",
                "name": "CLIENT_ID",
                "description": "PayPal client ID for alternative payment processing",
                "revenue_impact": "medium",
                "revenue_stream": "Product Sales",
                "priority": 7,
                "discovered_by": "System",
            },
            {
                "service": "paypal",
                "name": "CLIENT_SECRET",
                "description": "PayPal client secret for payment authentication",
                "revenue_impact": "medium",
                "revenue_stream": "Product Sales",
                "priority": 7,
                "discovered_by": "System",
            },
            {
                "service": "clickbank",
                "name": "API_KEY",
                "description": "ClickBank API key for affiliate product sales",
                "revenue_impact": "high",
                "revenue_stream": "Affiliate Marketing",
                "priority": 8,
                "discovered_by": "System",
            },
            {
                "service": "digistore24",
                "name": "API_KEY",
                "description": "DigiStore24 API key for digital product sales",
                "revenue_impact": "medium",
                "revenue_stream": "Product Sales",
                "priority": 6,
                "discovered_by": "System",
            },
            {
                "service": "shopify",
                "name": "ADMIN_API_KEY",
                "description": "Shopify admin API key for e-commerce operations",
                "revenue_impact": "medium",
                "revenue_stream": "E-commerce",
                "priority": 6,
                "discovered_by": "System",
            },
            {
                "service": "gumroad",
                "name": "API_KEY",
                "description": "Gumroad API key for digital product sales",
                "revenue_impact": "medium",
                "revenue_stream": "Product Sales",
                "priority": 5,
                "discovered_by": "System",
            },
            {
                "service": "twitter",
                "name": "API_KEY",
                "description": "Twitter API key for social media marketing and traffic generation",
                "revenue_impact": "medium",
                "revenue_stream": "Social Media Marketing",
                "priority": 6,
                "discovered_by": "System",
            },
            {
                "service": "linkedin",
                "name": "API_KEY",
                "description": "LinkedIn API key for B2B marketing and lead generation",
                "revenue_impact": "medium",
                "revenue_stream": "B2B Marketing",
                "priority": 6,
                "discovered_by": "System",
            },
            {
                "service": "facebook",
                "name": "ACCESS_TOKEN",
                "description": "Facebook access token for social media advertising",
                "revenue_impact": "high",
                "revenue_stream": "Paid Advertising",
                "priority": 8,
                "discovered_by": "System",
            },
            {
                "service": "google_ads",
                "name": "API_KEY",
                "description": "Google Ads API key for paid search advertising",
                "revenue_impact": "high",
                "revenue_stream": "Paid Advertising",
                "priority": 8,
                "discovered_by": "System",
            },
            {
                "service": "amazon_associates",
                "name": "ASSOCIATE_TAG",
                "description": "Amazon Associates tag for affiliate revenue",
                "revenue_impact": "medium",
                "revenue_stream": "Affiliate Marketing",
                "priority": 7,
                "discovered_by": "System",
            },
            {
                "service": "discord",
                "name": "BOT_TOKEN",
                "description": "Discord bot token for community engagement and marketing",
                "revenue_impact": "low",
                "revenue_stream": "Community Building",
                "priority": 4,
                "discovered_by": "System",
            },
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for suggestion in default_suggestions:
                cursor.execute("""
                    INSERT OR IGNORE INTO credential_suggestions
                    (service, name, description, revenue_impact, revenue_stream, priority, discovered_by, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'suggested', ?, ?)
                """, (
                    suggestion["service"],
                    suggestion["name"],
                    suggestion["description"],
                    suggestion["revenue_impact"],
                    suggestion["revenue_stream"],
                    suggestion["priority"],
                    suggestion["discovered_by"],
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            conn.commit()
    
    def add_suggestion(
        self,
        service: str,
        name: str,
        description: str,
        revenue_impact: str = "medium",
        revenue_stream: str = "General",
        priority: int = 5,
        discovered_by: str = "Agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Add a new credential suggestion"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO credential_suggestions
                (service, name, description, revenue_impact, revenue_stream, priority, discovered_by, status, metadata, discovered_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'suggested', ?, ?, ?, ?)
            """, (
                service,
                name,
                description,
                revenue_impact,
                revenue_stream,
                priority,
                discovered_by,
                json.dumps(metadata or {}),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "message": f"Suggestion added for {service}/{name}"}
    
    def get_suggestions(
        self,
        status: Optional[str] = None,
        revenue_stream: Optional[str] = None,
        min_priority: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get credential suggestions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM credential_suggestions WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            else:
                query += " AND status = 'suggested'"
            
            if revenue_stream:
                query += " AND revenue_stream = ?"
                params.append(revenue_stream)
            
            if min_priority:
                query += " AND priority >= ?"
                params.append(min_priority)
            
            query += " ORDER BY priority DESC, revenue_impact DESC, created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            suggestions = []
            for row in rows:
                suggestion = dict(row)
                suggestion["metadata"] = json.loads(suggestion.get("metadata") or "{}")
                suggestions.append(suggestion)
            
            return suggestions
    
    def mark_as_added(self, service: str, name: str) -> Dict:
        """Mark a suggestion as added (user has added the credential)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credential_suggestions
                SET status = 'added', updated_at = ?
                WHERE service = ? AND name = ?
            """, (datetime.now(timezone.utc).isoformat(), service, name))
            conn.commit()
            return {"success": True}
    
    def dismiss_suggestion(self, service: str, name: str) -> Dict:
        """Dismiss a suggestion"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credential_suggestions
                SET status = 'dismissed', updated_at = ?
                WHERE service = ? AND name = ?
            """, (datetime.now(timezone.utc).isoformat(), service, name))
            conn.commit()
            return {"success": True}
    
    def discover_revenue_stream_credentials(
        self,
        revenue_stream: str,
        required_credentials: List[Dict[str, str]],
        discovered_by: str = "Agent"
    ) -> Dict:
        """Discover and add credential suggestions for a new revenue stream"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store revenue stream mapping
            cursor.execute("""
                INSERT OR REPLACE INTO revenue_credential_mapping
                (revenue_stream, required_credentials, discovered_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                revenue_stream,
                json.dumps(required_credentials),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            
            # Add suggestions for each credential
            for cred in required_credentials:
                cursor.execute("""
                    INSERT OR IGNORE INTO credential_suggestions
                    (service, name, description, revenue_impact, revenue_stream, priority, discovered_by, status, discovered_at, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'suggested', ?, ?, ?)
                """, (
                    cred.get("service", "unknown"),
                    cred.get("name", "API_KEY"),
                    cred.get("description", f"Required for {revenue_stream} revenue stream"),
                    cred.get("revenue_impact", "medium"),
                    revenue_stream,
                    cred.get("priority", 5),
                    discovered_by,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            
            conn.commit()
            return {"success": True, "suggestions_added": len(required_credentials)}
