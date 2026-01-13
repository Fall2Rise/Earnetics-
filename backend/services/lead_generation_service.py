"""
Lead Generation & Acquisition Service
Scrapes targeted websites to find potential customers and build email lists.
"""
import re
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Email regex pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Common contact page indicators
CONTACT_INDICATORS = ['contact', 'about', 'team', 'founder', 'hello', 'reach', 'connect']


class LeadGenerationService:
    """Service for scraping websites and extracting lead information"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._ensure_tables()
        self.rate_limit_delay = 1.0  # Seconds between requests (optimized for higher volume)
        
    def _ensure_tables(self):
        """Create necessary database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Target websites configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lead_target_websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL UNIQUE,
                    base_url TEXT NOT NULL,
                    target_paths TEXT,  -- JSON array of paths to scrape
                    keywords TEXT,  -- JSON array of keywords to look for
                    enabled INTEGER DEFAULT 1,
                    last_scraped TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Scraped leads
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT,
                    website TEXT,
                    source_url TEXT NOT NULL,
                    source_domain TEXT NOT NULL,
                    context TEXT,  -- Context where email was found
                    qualified INTEGER DEFAULT 0,  -- 0=unqualified, 1=qualified
                    added_to_list INTEGER DEFAULT 0,  -- Whether added to email list
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(email, source_domain)
                )
            """)
            
            # Scraping history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT,  -- success, failed, blocked
                    leads_found INTEGER DEFAULT 0,
                    error_message TEXT,
                    scraped_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def add_target_website(self, domain: str, base_url: str, target_paths: List[str] = None, keywords: List[str] = None) -> Dict:
        """Add a target website for scraping"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            import json
            
            target_paths_json = json.dumps(target_paths or ['/contact', '/about', '/team'])
            keywords_json = json.dumps(keywords or [])
            
            try:
                cursor.execute("""
                    INSERT INTO lead_target_websites (domain, base_url, target_paths, keywords, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    domain,
                    base_url,
                    target_paths_json,
                    keywords_json,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                ))
                conn.commit()
                logger.info(f"✅ Added target website: {domain}")
                return {"status": "added", "domain": domain}
            except sqlite3.IntegrityError:
                # Update existing
                cursor.execute("""
                    UPDATE lead_target_websites
                    SET base_url = ?, target_paths = ?, keywords = ?, updated_at = ?, enabled = 1
                    WHERE domain = ?
                """, (base_url, target_paths_json, keywords_json, datetime.now(timezone.utc).isoformat(), domain))
                conn.commit()
                logger.info(f"✅ Updated target website: {domain}")
                return {"status": "updated", "domain": domain}
    
    def get_target_websites(self, enabled_only: bool = True) -> List[Dict]:
        """Get list of target websites"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM lead_target_websites"
            if enabled_only:
                query += " WHERE enabled = 1"
            query += " ORDER BY last_scraped ASC, created_at DESC"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def _check_robots_txt(self, base_url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            # Check if our user agent can access the base path
            return rp.can_fetch(self.session.headers['User-Agent'], base_url)
        except Exception as e:
            logger.debug(f"Could not check robots.txt for {base_url}: {e}")
            # If we can't check, assume it's allowed (but be respectful)
            return True
    
    def _extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract email addresses from text"""
        emails = set()
        for match in EMAIL_PATTERN.finditer(text):
            email = match.group().lower()
            # Filter out common non-personal emails
            if not any(skip in email for skip in ['noreply', 'no-reply', 'donotreply', 'example.com', 'test.com']):
                emails.add(email)
        return emails
    
    def _extract_contact_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract contact information from a page"""
        leads = []
        
        # Get all text content
        text_content = soup.get_text()
        
        # Extract emails
        emails = self._extract_emails_from_text(text_content)
        
        # Try to find names near emails
        for email in emails:
            lead = {
                "email": email,
                "name": None,
                "website": urlparse(url).netloc,
                "source_url": url,
                "source_domain": urlparse(url).netloc,
                "context": None,
            }
            
            # Try to find name near email
            email_index = text_content.lower().find(email)
            if email_index > 0:
                # Look for name patterns before email
                context_start = max(0, email_index - 200)
                context_end = min(len(text_content), email_index + 200)
                context = text_content[context_start:context_end]
                
                # Look for common name patterns
                name_patterns = [
                    r'(?:Founder|CEO|Founder & CEO|Co-Founder|President|Director|Manager|Lead|Head)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                    r'([A-Z][a-z]+\s+[A-Z][a-z]+)[\s,]+(?:Founder|CEO|Co-Founder)',
                    r'Contact[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, context, re.IGNORECASE)
                    if match:
                        lead["name"] = match.group(1).strip()
                        break
                
                lead["context"] = context.strip()[:500]  # Store context
            
            leads.append(lead)
        
        return leads
    
    def scrape_website(self, domain: str, max_pages: int = 20) -> Dict:
        """Scrape a target website for leads"""
        target = None
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lead_target_websites WHERE domain = ? AND enabled = 1", (domain,))
            target = cursor.fetchone()
        
        if not target:
            return {"error": f"Target website {domain} not found or disabled"}
        
        target = dict(target)
        import json
        target_paths = json.loads(target.get("target_paths", "[]") or "[]")
        keywords = json.loads(target.get("keywords", "[]") or "[]")
        base_url = target["base_url"]
        
        # Check robots.txt
        if not self._check_robots_txt(base_url):
            logger.warning(f"⚠️ robots.txt blocks scraping for {domain}")
            return {"error": "robots.txt blocks scraping", "domain": domain}
        
        all_leads = []
        pages_scraped = 0
        
        # Scrape target paths
        urls_to_scrape = [urljoin(base_url, path) for path in target_paths]
        
        # Also try common contact pages
        if not urls_to_scrape:
            urls_to_scrape = [urljoin(base_url, path) for path in ['/contact', '/about', '/team', '/']]
        
        for url in urls_to_scrape[:max_pages]:
            try:
                time.sleep(self.rate_limit_delay)  # Rate limiting
                
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                leads = self._extract_contact_info(soup, url)
                
                if leads:
                    all_leads.extend(leads)
                    pages_scraped += 1
                    
                    # Log scraping
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO scraping_history (domain, url, status, leads_found, scraped_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (domain, url, "success", len(leads), datetime.now(timezone.utc).isoformat()))
                        conn.commit()
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                # Log error
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO scraping_history (domain, url, status, error_message, scraped_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (domain, url, "failed", str(e), datetime.now(timezone.utc).isoformat()))
                    conn.commit()
        
        # Save leads to database
        saved_count = 0
        for lead in all_leads:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO scraped_leads (email, name, website, source_url, source_domain, context, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lead["email"],
                        lead.get("name"),
                        lead.get("website"),
                        lead["source_url"],
                        lead["source_domain"],
                        lead.get("context"),
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()
                    saved_count += 1
            except sqlite3.IntegrityError:
                # Lead already exists
                pass
        
        # Update last_scraped
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lead_target_websites
                SET last_scraped = ?, updated_at = ?
                WHERE domain = ?
            """, (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), domain))
            conn.commit()
        
        logger.info(f"✅ Scraped {domain}: Found {saved_count} new leads from {pages_scraped} pages")
        
        return {
            "domain": domain,
            "pages_scraped": pages_scraped,
            "leads_found": len(all_leads),
            "leads_saved": saved_count,
            "leads": all_leads[:10]  # Return first 10 for preview
        }
    
    def get_scraped_leads(self, limit: int = 100, qualified_only: bool = False) -> List[Dict]:
        """Get scraped leads"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM scraped_leads"
            if qualified_only:
                query += " WHERE qualified = 1"
            query += " ORDER BY created_at DESC LIMIT ?"
            
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def qualify_lead(self, lead_id: int, qualified: bool = True) -> Dict:
        """Mark a lead as qualified or unqualified"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scraped_leads
                SET qualified = ?, updated_at = ?
                WHERE id = ?
            """, (1 if qualified else 0, datetime.now(timezone.utc).isoformat(), lead_id))
            conn.commit()
            return {"status": "updated", "lead_id": lead_id, "qualified": qualified}
    
    def add_leads_to_email_list(self, lead_ids: List[int] = None) -> Dict:
        """Add qualified leads to the email marketing list"""
        from backend.services.mailops_service import MailOpsService, Subscriber
        
        mailops = MailOpsService()
        added_count = 0
        skipped_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if lead_ids:
                placeholders = ','.join(['?'] * len(lead_ids))
                cursor.execute(f"""
                    SELECT * FROM scraped_leads
                    WHERE id IN ({placeholders}) AND (qualified = 1 OR qualified = 0)
                """, lead_ids)
            else:
                # Add all qualified leads that haven't been added yet
                cursor.execute("""
                    SELECT * FROM scraped_leads
                    WHERE qualified = 1 AND added_to_list = 0
                """)
            
            leads = [dict(row) for row in cursor.fetchall()]
            
            for lead in leads:
                try:
                    subscriber = Subscriber(
                        email=lead["email"],
                        first_name=lead.get("name"),
                        status="active",
                        source=f"scraped_{lead['source_domain']}",
                        tags=["scraped_lead", lead.get("source_domain", "unknown")]
                    )
                    mailops.add_subscriber(subscriber)
                    
                    # Mark as added
                    cursor.execute("""
                        UPDATE scraped_leads
                        SET added_to_list = 1, updated_at = ?
                        WHERE id = ?
                    """, (datetime.now(timezone.utc).isoformat(), lead["id"]))
                    added_count += 1
                except Exception as e:
                    logger.debug(f"Could not add lead {lead['email']} to list: {e}")
                    skipped_count += 1
            
            conn.commit()
        
        logger.info(f"✅ Added {added_count} leads to email list (skipped {skipped_count})")
        return {
            "added": added_count,
            "skipped": skipped_count,
            "total_leads": len(leads)
        }
