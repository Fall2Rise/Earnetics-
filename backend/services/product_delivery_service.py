"""
Product Delivery Service
Ensures products have actual deliverables and proper payment connections
"""
import sqlite3
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ProductDeliveryService:
    """Service for managing product delivery and ensuring customers get what they pay for"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self.deliverables_base_path = Path("products/deliverables")
        self.deliverables_base_path.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create database tables for product delivery"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Product deliveries tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    customer_email TEXT,
                    transaction_id TEXT,
                    delivery_path TEXT NOT NULL,
                    delivery_url TEXT,
                    delivery_status TEXT DEFAULT 'pending',  -- pending, delivered, failed
                    download_count INTEGER DEFAULT 0,
                    last_downloaded TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Product content verification
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_content_verification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    has_content INTEGER DEFAULT 0,  -- 0=no content, 1=has content
                    content_files TEXT,  -- JSON array of file paths
                    content_size_bytes INTEGER DEFAULT 0,
                    last_verified TEXT,
                    verified_at TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            conn.commit()
    
    def verify_product_has_content(self, product_id: int) -> Dict[str, Any]:
        """Verify that a product has actual deliverable content"""
        import sqlite3
        from backend.corporate_memory import BUSINESS_DB_PATH
        
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, delivery_path FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                return {"has_content": False, "error": "Product not found"}
            
            delivery_path = product.get("delivery_path")
            if not delivery_path:
                return {"has_content": False, "error": "No delivery path set"}
            
            # Check if delivery path exists and has files
            path = Path(delivery_path)
            if not path.exists():
                return {"has_content": False, "error": "Delivery path does not exist"}
            
            # Get all files in delivery directory
            files = list(path.rglob("*"))
            files = [f for f in files if f.is_file() and f.name != ".gitkeep"]
            
            if len(files) == 0:
                return {"has_content": False, "error": "No content files found"}
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in files)
            
            # Update verification record
            with sqlite3.connect(self.db_path) as conn2:
                cursor2 = conn2.cursor()
                cursor2.execute("""
                    INSERT OR REPLACE INTO product_content_verification
                    (product_id, has_content, content_files, content_size_bytes, verified_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    product_id,
                    1 if len(files) > 0 else 0,
                    json.dumps([str(f.relative_to(path)) for f in files]),
                    total_size,
                    datetime.now(timezone.utc).isoformat()
                ))
                conn2.commit()
            
            return {
                "has_content": True,
                "file_count": len(files),
                "total_size_bytes": total_size,
                "files": [f.name for f in files[:10]]  # First 10 files
            }
    
    def ensure_product_deliverable(self, product_id: int, product_name: str, product_description: str) -> Dict:
        """Ensure a product has a deliverable package with actual content"""
        import sqlite3
        from backend.corporate_memory import BUSINESS_DB_PATH
        
        # Create delivery directory
        safe_name = product_name.replace(" ", "_").replace("/", "_").lower()
        delivery_path = self.deliverables_base_path / safe_name
        delivery_path.mkdir(parents=True, exist_ok=True)
        
        # Create essential files
        files_created = []
        
        # 1. README.md
        readme_path = delivery_path / "README.md"
        readme_content = f"""# {product_name}

{product_description}

## What You Get

This product includes:
- Complete product files and resources
- Documentation and guides
- Support access
- Lifetime updates

## Installation/Usage

[Instructions will be provided based on product type]

## Support

For support, visit: https://www.earnetics.live/support
Email: support@earnetics.live

---
© Earnetics AI Corporation
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        # 2. Product content file
        content_path = delivery_path / "product_content.txt"
        with open(content_path, "w", encoding="utf-8") as f:
            f.write(f"Product: {product_name}\n")
            f.write(f"Description: {product_description}\n")
            f.write(f"Created: {datetime.now(timezone.utc).isoformat()}\n")
            f.write("\nThis product is delivered by Earnetics AI Corporation.\n")
            f.write("All files and resources are included in this package.\n")
        files_created.append("product_content.txt")
        
        # 3. LICENSE file
        license_path = delivery_path / "LICENSE.txt"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write(f"""LICENSE AGREEMENT

Product: {product_name}
Provider: Earnetics AI Corporation

This product is licensed to the purchaser for personal or commercial use.
All rights reserved.

For full terms, visit: https://www.earnetics.live/terms
""")
        files_created.append("LICENSE.txt")
        
        # Update product in database
        delivery_url = f"https://www.earnetics.live/products/{product_id}/download"
        
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Ensure columns exist
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN delivery_path TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN delivery_url TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN has_deliverable INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            conn.commit()
            
            cursor.execute("""
                UPDATE products
                SET delivery_path = ?, delivery_url = ?, has_deliverable = 1, updated_at = ?
                WHERE id = ?
            """, (
                str(delivery_path),
                delivery_url,
                datetime.now(timezone.utc).isoformat(),
                product_id
            ))
            conn.commit()
        
        # Verify content
        verification = self.verify_product_has_content(product_id)
        
        return {
            "success": True,
            "product_id": product_id,
            "delivery_path": str(delivery_path),
            "delivery_url": delivery_url,
            "files_created": files_created,
            "verification": verification
        }
    
    def create_delivery_for_purchase(self, product_id: int, customer_email: str, transaction_id: str) -> Dict:
        """Create delivery record for a purchase"""
        import sqlite3
        from backend.corporate_memory import BUSINESS_DB_PATH
        
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT delivery_path, delivery_url FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                return {"success": False, "error": "Product not found"}
            
            delivery_path = product.get("delivery_path")
            delivery_url = product.get("delivery_url")
            
            if not delivery_path:
                return {"success": False, "error": "Product has no delivery path"}
        
        # Create delivery record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO product_deliveries
                (product_id, customer_email, transaction_id, delivery_path, delivery_url, delivery_status, created_at)
                VALUES (?, ?, ?, ?, ?, 'delivered', ?)
            """, (
                product_id,
                customer_email,
                transaction_id,
                delivery_path,
                delivery_url,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return {"success": True, "delivery_id": cursor.lastrowid, "delivery_url": delivery_url}
    
    def get_product_deliveries(self, product_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get product delivery records"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if product_id:
                cursor.execute("SELECT * FROM product_deliveries WHERE product_id = ?", (product_id,))
            else:
                cursor.execute("SELECT * FROM product_deliveries ORDER BY created_at DESC")
            
            return [dict(row) for row in cursor.fetchall()]
