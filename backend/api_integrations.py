"""
Real API Integration System
Handles actual connections to external services
"""
import os
import json
from typing import Any, Dict, List, Optional
import stripe
import httpx
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def audit_event(action: str, *, status: str = "success", message: Optional[str] = None, **details: Any) -> None:
    log_event(f"integration.{action}", status=status, message=message, **details)

try:
    from backend.credentials_store import get_secret, describe_secrets
except ModuleNotFoundError:  # pragma: no cover - legacy path fallback
    from credentials_store import get_secret, describe_secrets

from backend.llm_client import LLMGenerationError, LLMNotConfiguredError, LLMClient
from backend.integration_registry import summarize_connectors
from backend.audit_log import log_event
class StripeIntegration:
    """Real Stripe payment processing"""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or get_secret("STRIPE_SECRET_KEY")
        if self.api_key:
            stripe.api_key = self.api_key
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Stripe API key not found. Set STRIPE_SECRET_KEY environment variable.")

    async def create_product(self, name: str, description: str, price: float) -> Dict:
        """Create actual Stripe product"""
        if not self.enabled:
            audit_event(
                "stripe.create_product",
                status="error",
                message="not configured",
                name=name,
                amount=price,
            )
            return {"error": "Stripe not configured"}

        try:
            product = stripe.Product.create(name=name, description=description)
            price_obj = stripe.Price.create(
                product=product.id,
                unit_amount=int(price * 100),
                currency="usd",
            )
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price_obj.id, "quantity": 1}],
            )
            audit_event(
                "stripe.create_product",
                product_id=product.id,
                price_id=price_obj.id,
                amount=price,
                name=name,
            )
            return {
                "product_id": product.id,
                "price_id": price_obj.id,
                "payment_link": payment_link.url,
                "status": "live",
            }
        except stripe.error.StripeError as exc:
            logger.error("Stripe error: %s", exc)
            audit_event(
                "stripe.create_product",
                status="error",
                message=str(exc),
                name=name,
            )
            return {"error": str(exc)}

    async def get_recent_payments(self, limit: int = 10) -> List[Dict]:
        """Get recent payment transactions"""
        if not self.enabled:
            audit_event(
                "stripe.list_payments",
                status="error",
                message="not configured",
                limit=limit,
            )
            return []

        try:
            charges = stripe.Charge.list(limit=limit)
            payments: List[Dict] = []
            for charge in charges.data:
                payments.append(
                    {
                        "id": charge.id,
                        "amount": charge.amount / 100,
                        "currency": charge.currency,
                        "status": charge.status,
                        "created": datetime.fromtimestamp(charge.created).isoformat(),
                        "description": charge.description,
                    }
                )
            audit_event(
                "stripe.list_payments",
                count=len(payments),
                limit=limit,
            )
            return payments
        except stripe.error.StripeError as exc:
            logger.error("Stripe error: %s", exc)
            audit_event(
                "stripe.list_payments",
                status="error",
                message=str(exc),
                limit=limit,
            )
            return []


class ContentGenerationIntegration:
    """LLM-backed content generation (defaults to local Ollama)."""
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        self._client = LLMClient(provider=self.provider, model=model)
        self.enabled = self._client.configured
        self._init_error = self._client.init_error
        if not self.enabled:
            message = self._init_error or "LLM provider not configured"
            logger.warning(message)
    async def generate_product_content(self, topic: str, product_type: str) -> Dict:
        """Generate product content using the configured LLM."""
        if not self.enabled:
            audit_event(
                "llm.generate_product_content",
                status="error",
                message=self._init_error or "LLM provider not configured",
                topic=topic,
                product_type=product_type,
            )
            return {"error": self._init_error or "LLM provider not configured"}
        prompts = {
            "ebook": f"Create a comprehensive outline for an ebook about {topic}. Include 5 chapter titles and brief descriptions.",
            "course": f"Design a complete online course about {topic}. Include modules, lessons, and learning objectives.",
            "software": f"Plan a software tool for {topic}. Include features, user interface design, and technical requirements.",
        }
        system_prompt = (
            "You are a product development expert who creates detailed, actionable content outlines."
        )
        user_prompt = prompts.get(product_type, prompts["ebook"])
        try:
            response = await self._client.generate(
                system_prompt,
                user_prompt,
                max_tokens=1000,
                temperature=0.7,
            )
            result = {
                "content": response.content,
                "provider": self.provider,
            }
            audit_event(
                "llm.generate_product_content",
                topic=topic,
                product_type=product_type,
            )
            return result
        except (LLMGenerationError, LLMNotConfiguredError) as exc:
            audit_event(
                "llm.generate_product_content",
                status="error",
                message=str(exc),
                topic=topic,
                product_type=product_type,
            )
            return {"error": str(exc)}
    async def generate_marketing_copy(
        self, product_name: str, target_audience: str
    ) -> Dict:
        """Generate marketing copy and sales pages."""
        if not self.enabled:
            return {"error": self._init_error or "LLM provider not configured"}
        system_prompt = (
            "You are a direct response copywriter who creates high-converting sales copy."
        )
        user_prompt = f"""
        Create compelling marketing copy for "{product_name}" targeted at {target_audience}.
        Include:
        1. Attention-grabbing headline
        2. Problem statement
        3. Solution overview
        4. Three key benefits
        5. Call to action
        Make it persuasive and conversion-focused.
        """
        try:
            response = await self._client.generate(
                system_prompt,
                user_prompt,
                max_tokens=800,
                temperature=0.8,
            )
            return {
                "marketing_copy": response.content,
                "provider": self.provider,
            }
        except (LLMGenerationError, LLMNotConfiguredError) as exc:
            return {"error": str(exc)}
class EmailMarketingIntegration:
    """Real email marketing automation"""
    def __init__(self, smtp_server: str = "smtp.gmail.com", port: int = 587):
        configured_server = get_secret("SMTP_SERVER", default=smtp_server)
        configured_port = get_secret("SMTP_PORT", default=str(port))
        self.smtp_server = configured_server or smtp_server
        try:
            self.port = int(configured_port) if configured_port else port
        except ValueError:
            self.port = port
        self.email = get_secret("SMTP_EMAIL")
        self.password = get_secret("SMTP_PASSWORD")
        self.enabled = bool(self.email and self.password)
        if not self.enabled:
            logger.warning("Email credentials not found. Set SMTP_EMAIL and SMTP_PASSWORD environment variables.")
    async def send_promotional_email(
        self, recipients: List[str], subject: str, content: str
    ) -> Dict:
        """Send actual promotional emails"""
        if not self.enabled:
            audit_event(
                "email.send_promotional",
                status="error",
                message="not configured",
                recipients=len(recipients),
            )
            return {"error": "Email not configured"}
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["Subject"] = subject
            msg.attach(MIMEText(content, "html"))
            results = {"sent": 0, "failed": 0, "errors": []}
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email, self.password)
                for recipient in recipients:
                    try:
                        msg["To"] = recipient
                        server.send_message(msg)
                        results["sent"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"{recipient}: {str(e)}")
            return results
        except Exception as e:
            return {"error": str(e)}
    async def create_email_sequence(self, product_name: str) -> List[Dict]:
        """Create automated email sequence"""
        sequence = [
            {
                "day": 0,
                "subject": f"Welcome! Your {product_name} journey starts now",
                "content": f"Thank you for your interest in {product_name}! Here's what you can expect...",
            },
            {
                "day": 1,
                "subject": f"The #1 mistake people make with {product_name}",
                "content": f"Most people fail with {product_name} because they make this crucial mistake...",
            },
            {
                "day": 3,
                "subject": f"Last chance: {product_name} special offer ends soon",
                "content": f"This exclusive offer for {product_name} expires in 24 hours...",
            },
        ]
        audit_event("email.create_sequence", count=len(sequence), product_name=product_name)
        return sequence
class SocialMediaIntegration:
    """Social automation wrapper (currently supports X/Twitter)."""

    def __init__(self) -> None:
        self.twitter_api_key = get_secret("TWITTER_API_KEY")
        self.twitter_api_secret = get_secret("TWITTER_API_SECRET")
        self.twitter_access_token = get_secret("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = get_secret("TWITTER_ACCESS_SECRET")
        self.enabled = all(
            [
                self.twitter_api_key,
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_secret,
            ]
        )
        if not self.enabled:
            logger.warning("Twitter API credentials not found. Set TWITTER_* environment variables.")

    async def post_to_twitter(self, content: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Twitter not configured"}
        try:
            import tweepy

            auth = tweepy.OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
            auth.set_access_token(self.twitter_access_token, self.twitter_access_secret)
            api = tweepy.API(auth)
            tweet = api.update_status(content)
            return {"tweet_id": tweet.id, "url": f"https://twitter.com/user/status/{tweet.id}", "posted_at": tweet.created_at.isoformat()}
        except Exception as exc:  # pragma: no cover - network failure
            return {"error": str(exc)}

    async def generate_social_content(self, product_name: str, platform: str) -> List[str]:
        templates = {
            "twitter": [
                f"Breaking down the fastest path to success with {product_name}. Thread below.",
                f"Pro tip: the secret to {product_name} success is rarely obvious.",
                f"Three {product_name} strategies that worked this quarter:",
                f"If you are serious about {product_name}, start with this playbook.",
            ],
            "linkedin": [
                f"Working with teams revealed the top three {product_name} challenges:",
                f"The {product_name} landscape changed dramatically this year. Here is what to watch:",
                f"Most {product_name} advice is outdated. This plan still wins in 2025:",
                f"I just published a new guide on {product_name}. Key insights inside:",
            ],
        }
        return templates.get(platform, templates["twitter"])


class MarketResearchIntegration:
    """Real market research and trend analysis"""
    def __init__(self):
        self.google_trends_available = True
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl="en-US", tz=360)
        except ImportError:
            self.google_trends_available = False
            logger.warning("Install pytrends for Google Trends integration: pip install pytrends")
    async def analyze_keyword_trends(self, keywords: List[str]) -> Dict:
        """Get real Google Trends data"""
        if not self.google_trends_available:
            return {"error": "Google Trends not available"}
        try:
            self.pytrends.build_payload(
                keywords, cat=0, timeframe="today 12-m", geo="", gprop=""
            )
            # Interest over time
            interest_data = self.pytrends.interest_over_time()
            # Related queries
            related_queries = self.pytrends.related_queries()
            return {
                "keywords": keywords,
                "trend_data": interest_data.to_dict()
                if not interest_data.empty
                else {},
                "related_queries": related_queries,
                "analysis_date": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}
    async def get_competitor_analysis(self, niche: str) -> Dict:
        """Analyze competitive landscape"""
        # This would integrate with SEMrush, Ahrefs, etc. in production
        return {
            "niche": niche,
            "competition_level": "medium",
            "top_competitors": [
                {"name": "Competitor A", "traffic": "50K/month", "strength": "high"},
                {"name": "Competitor B", "traffic": "30K/month", "strength": "medium"},
                {"name": "Competitor C", "traffic": "20K/month", "strength": "low"},
            ],
            "opportunity_score": 0.75,
            "recommended_strategy": "content marketing + paid ads",
        }


class AffiliateNetworkIntegration:
    """Connects to affiliate networks for offer discovery and tracking."""

    def __init__(self) -> None:
        self.api_base_url = get_secret("AFFILIATE_API_BASE_URL") or os.getenv("AFFILIATE_API_BASE_URL")
        self.api_key = get_secret("AFFILIATE_API_KEY") or os.getenv("AFFILIATE_API_KEY")
        self.program_id = get_secret("AFFILIATE_PROGRAM_ID") or os.getenv("AFFILIATE_PROGRAM_ID")
        self.enabled = bool(self.api_base_url and self.api_key)
        self.timeout = float(os.getenv("AFFILIATE_API_TIMEOUT", "20"))

    async def fetch_top_offers(self, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        if not self.enabled:
            audit_event(
                "affiliate.fetch_offers",
                status="error",
                message="not configured",
                category=category,
                limit=limit,
            )
            return {"success": False, "offers": self._load_local_offers(limit, category), "error": "Affiliate API not configured"}
        params: Dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = category
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(base_url=self.api_base_url, timeout=self.timeout) as client:
                response = await client.get("/offers", params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Affiliate offer fetch failed: %s", exc)
            audit_event(
                "affiliate.fetch_offers",
                status="error",
                message=str(exc),
                category=category,
                limit=limit,
            )
            return {"success": False, "offers": self._load_local_offers(limit, category), "error": str(exc)}
        offers = data.get("offers") or data
        audit_event(
            "affiliate.fetch_offers",
            category=category,
            limit=limit,
            count=len(offers) if isinstance(offers, list) else None,
        )
        return {"success": True, "offers": offers}

    async def create_tracking_link(self, offer_id: str, sub_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.enabled:
            audit_event(
                "affiliate.create_tracking",
                status="error",
                message="not configured",
                offer_id=offer_id,
                sub_id=sub_id,
            )
            return {"success": False, "error": "Affiliate API not configured"}
        payload: Dict[str, Any] = {"offer_id": offer_id}
        if sub_id:
            payload["sub_id"] = sub_id
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(base_url=self.api_base_url, timeout=self.timeout) as client:
                response = await client.post("/tracking-links", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Affiliate tracking link creation failed: %s", exc)
            audit_event(
                "affiliate.create_tracking",
                status="error",
                message=str(exc),
                offer_id=offer_id,
                sub_id=sub_id,
            )
            return {"success": False, "error": str(exc)}
        audit_event(
            "affiliate.create_tracking",
            offer_id=offer_id,
            sub_id=sub_id,
        )
        return {"success": True, "tracking_link": data.get("tracking_link") or data}

    async def fetch_program_performance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        if not self.enabled:
            audit_event(
                "affiliate.performance",
                status="error",
                message="not configured",
                start=start_date,
                end=end_date,
            )
            return {"success": False, "error": "Affiliate API not configured"}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"program_id": self.program_id, "start": start_date, "end": end_date}
        try:
            async with httpx.AsyncClient(base_url=self.api_base_url, timeout=self.timeout) as client:
                response = await client.get("/performance", params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Affiliate performance fetch failed: %s", exc)
            audit_event(
                "affiliate.performance",
                status="error",
                message=str(exc),
                start=start_date,
                end=end_date,
            )
            return {"success": False, "error": str(exc)}
        audit_event(
            "affiliate.performance",
            start=start_date,
            end=end_date,
        )
        return {"success": True, "performance": data}

    def _load_local_offers(self, limit: int, category: Optional[str]) -> List[Dict[str, Any]]:
        sample_path = Path("data/products.json")
        if sample_path.exists():
            try:
                products = json.loads(sample_path.read_text())
                offers: List[Dict[str, Any]] = []
                for item in products:
                    name = item.get("name") or "Affiliate Offer"
                    if category and category.lower() not in name.lower():
                        continue
                    offers.append({
                        "id": f"local-{item.get('id', name)}",
                        "name": name,
                        "payout": round((item.get("price", 0) or 0) * 0.3, 2),
                        "category": category or "general",
                        "landing_page": item.get("landing_page", "https://example.com"),
                    })
                return offers[:limit]
            except Exception as exc:  # pragma: no cover - parsing issue
                logger.debug("Failed to load local offers: %s", exc)
        return [{"id": "fallback-offer", "name": "High-Ticket Automation Course", "payout": 197.0, "category": category or "automation", "landing_page": "https://example.com/automation"}]


class DropshippingStoreIntegration:
    """Dropshipping store automation (Shopify by default)."""

    def __init__(self) -> None:
        self.provider = (get_secret("DROPSHIPPING_PROVIDER") or os.getenv("DROPSHIPPING_PROVIDER") or "shopify").lower()
        self.store_url = get_secret("SHOPIFY_STORE_URL") or os.getenv("SHOPIFY_STORE_URL")
        self.admin_token = get_secret("SHOPIFY_ADMIN_API_TOKEN") or os.getenv("SHOPIFY_ADMIN_API_TOKEN")
        self.api_version = os.getenv("SHOPIFY_API_VERSION", "2024-01")
        self.enabled = bool(self.store_url and self.admin_token)
        self.timeout = float(os.getenv("DROPSHIPPING_API_TIMEOUT", "20"))

    async def list_products(self, limit: int = 25) -> Dict[str, Any]:
        if not self.enabled or self.provider != "shopify":
            audit_event(
                "dropshipping.list_products",
                status="error",
                message="not configured",
                provider=self.provider,
                limit=limit,
            )
            return {"success": False, "products": self._load_local_products(limit), "error": "Dropshipping store not configured"}
        headers = {"X-Shopify-Access-Token": self.admin_token}
        endpoint = f"/admin/api/{self.api_version}/products.json"
        params = {"limit": limit}
        try:
            async with httpx.AsyncClient(base_url=self.store_url, timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Shopify product fetch failed: %s", exc)
            audit_event(
                "dropshipping.list_products",
                status="error",
                message=str(exc),
                provider=self.provider,
                limit=limit,
            )
            return {"success": False, "products": self._load_local_products(limit), "error": str(exc)}
        products = data.get("products", [])
        audit_event(
            "dropshipping.list_products",
            provider=self.provider,
            limit=limit,
            count=len(products) if isinstance(products, list) else None,
        )
        return {"success": True, "products": products}

    async def sync_product_listing(self, product: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or self.provider != "shopify":
            audit_event(
                "dropshipping.sync_product",
                status="error",
                message="not configured",
                provider=self.provider,
            )
            return {"success": False, "error": "Dropshipping store not configured"}
        headers = {"X-Shopify-Access-Token": self.admin_token, "Content-Type": "application/json"}
        endpoint = f"/admin/api/{self.api_version}/products.json"
        payload = {"product": product}
        try:
            async with httpx.AsyncClient(base_url=self.store_url, timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Shopify product sync failed: %s", exc)
            audit_event(
                "dropshipping.sync_product",
                status="error",
                message=str(exc),
                provider=self.provider,
            )
            return {"success": False, "error": str(exc)}
        audit_event("dropshipping.sync_product", provider=self.provider)
        return {"success": True, "product": data.get("product", data)}

    async def create_fulfillment_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or self.provider != "shopify":
            audit_event(
                "dropshipping.create_order",
                status="error",
                message="not configured",
                provider=self.provider,
            )
            return {"success": False, "error": "Dropshipping store not configured"}
        headers = {"X-Shopify-Access-Token": self.admin_token, "Content-Type": "application/json"}
        endpoint = f"/admin/api/{self.api_version}/orders.json"
        try:
            async with httpx.AsyncClient(base_url=self.store_url, timeout=self.timeout) as client:
                response = await client.post(endpoint, json={"order": order_payload}, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Shopify order creation failed: %s", exc)
            audit_event(
                "dropshipping.create_order",
                status="error",
                message=str(exc),
                provider=self.provider,
            )
            return {"success": False, "error": str(exc)}
        audit_event("dropshipping.create_order", provider=self.provider)
        return {"success": True, "order": data.get("order", data)}

    async def fetch_open_orders(self, limit: int = 25) -> Dict[str, Any]:
        if not self.enabled or self.provider != "shopify":
            audit_event(
                "dropshipping.list_orders",
                status="error",
                message="not configured",
                provider=self.provider,
                limit=limit,
            )
            return {"success": False, "orders": [], "error": "Dropshipping store not configured"}
        headers = {"X-Shopify-Access-Token": self.admin_token}
        endpoint = f"/admin/api/{self.api_version}/orders.json"
        params = {"status": "open", "limit": limit}
        try:
            async with httpx.AsyncClient(base_url=self.store_url, timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Shopify open order fetch failed: %s", exc)
            audit_event(
                "dropshipping.list_orders",
                status="error",
                message=str(exc),
                provider=self.provider,
                limit=limit,
            )
            return {"success": False, "orders": [], "error": str(exc)}
        orders = data.get("orders", [])
        audit_event(
            "dropshipping.list_orders",
            provider=self.provider,
            limit=limit,
            count=len(orders) if isinstance(orders, list) else None,
        )
        return {"success": True, "orders": orders}

    def _load_local_products(self, limit: int) -> List[Dict[str, Any]]:
        sample_path = Path("data/products.json")
        if sample_path.exists():
            try:
                products = json.loads(sample_path.read_text())
                return products[:limit]
            except Exception as exc:  # pragma: no cover - parsing issue
                logger.debug("Failed to load local products: %s", exc)
        return [{"title": "AI Automation Blueprint", "body_html": "<p>Digital training for automation agencies.</p>", "vendor": "AI Revenue Command Center", "product_type": "Digital"}]


class RevenueInnovationIntegration:
    """LLM-driven ideation for new revenue streams."""

    def __init__(self) -> None:
        self.llm_client = LLMClient(provider=os.getenv("LLM_PROVIDER", "ollama"))
        self.enabled = self.llm_client.configured
        self.init_error = self.llm_client.init_error
        if not self.enabled:
            logger.warning(self.init_error or "LLM provider not configured for innovation pipeline")

    async def propose_streams(self, company_context: Dict[str, Any], count: int = 5) -> Dict[str, Any]:
        if not self.enabled:
            return {"success": False, "error": self.init_error or "LLM provider not configured"}
        system_prompt = "You are the Chief Innovation Officer for a portfolio of AI-driven businesses."
        user_prompt = (
            "Based on the following context, propose unique revenue streams."
            " Return strict JSON with a list named streams where each stream has"
            " name, description, estimated_setup_time_days, required_integrations, and projected_monthly_revenue.\n"
            f"Context: {json.dumps(company_context, ensure_ascii=False)}\n"
            f"Number of streams: {count}"
        )
        try:
            response = await self.llm_client.generate(system_prompt, user_prompt, temperature=0.6, max_tokens=1200)
            raw_content = response.content.strip()
            try:
                parsed = json.loads(raw_content)
            except json.JSONDecodeError:
                parsed = {"streams": self._fallback_parse(raw_content)}
            return {"success": True, "streams": parsed.get("streams", []), "raw": raw_content}
        except (LLMGenerationError, LLMNotConfiguredError) as exc:
            return {"success": False, "error": str(exc)}

    def _fallback_parse(self, text: str) -> List[Dict[str, Any]]:
        streams: List[Dict[str, Any]] = []
        for line in text.splitlines():
            cleaned = line.strip('- *')
            if not cleaned:
                continue
            streams.append({
                "name": cleaned[:80],
                "description": cleaned,
                "estimated_setup_time_days": 30,
                "required_integrations": ["manual_review"],
                "projected_monthly_revenue": 1000,
            })
        return streams

class APIIntegrationManager:
    """Manages all API integrations"""
    def __init__(self):
        self.stripe = StripeIntegration()
        self.llm = ContentGenerationIntegration()
        self.email = EmailMarketingIntegration()
        self.social = SocialMediaIntegration()
        self.market_research = MarketResearchIntegration()
        self.affiliate = AffiliateNetworkIntegration()
        self.dropshipping = DropshippingStoreIntegration()
        self.innovation = RevenueInnovationIntegration()
    def get_integration_status(self) -> Dict[str, Any]:
        """Check status of all integrations"""
        credential_keys = [
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "PAYPAL_CLIENT_ID",
            "PAYPAL_CLIENT_SECRET",
            "SMTP_SERVER",
            "SMTP_EMAIL",
            "SMTP_PASSWORD",
            "LLM_PROVIDER",
            "TWITTER_API_KEY",
            "AFFILIATE_API_BASE_URL",
            "AFFILIATE_API_KEY",
            "SHOPIFY_STORE_URL",
            "SHOPIFY_ADMIN_API_TOKEN",
            "DROPSHIPPING_PROVIDER",
            "CLICKBANK_API_KEY",
            "CLICKBANK_API_SECRET",
            "DIGISTORE24_API_KEY",
            "GUMROAD_ACCESS_TOKEN",
        ]
        credentials_overview = describe_secrets(credential_keys)
        registry_overview = summarize_connectors()
        return {
            "stripe": {"enabled": self.stripe.enabled},
            "llm": {"enabled": self.llm.enabled},
            "email": {"enabled": self.email.enabled},
            "social_media": {"enabled": self.social.enabled},
            "market_research": {"enabled": self.market_research.google_trends_available},
            "affiliate": {"enabled": self.affiliate.enabled},
            "dropshipping": {"enabled": self.dropshipping.enabled},
            "innovation": {"enabled": self.innovation.enabled},
            "credentials": credentials_overview,
            "registry": registry_overview,
        }
    async def execute_full_product_launch(self, opportunity: Dict) -> Dict:
        """Execute complete product launch using all integrations"""
        results = {
            "opportunity": opportunity["keyword"],
            "launch_steps": {},
            "total_revenue_potential": 0,
        }
        # Step 1: Generate product content
        if self.llm.enabled:
            content = await self.llm.generate_product_content(
                opportunity["keyword"], "ebook"
            )
            results["launch_steps"]["content_generation"] = content
        # Step 2: Create Stripe product
        if self.stripe.enabled:
            product_name = f"{opportunity['keyword']} Mastery Guide"
            stripe_product = await self.stripe.create_product(
                product_name, f"Complete guide to {opportunity['keyword']}", 97.0
            )
            results["launch_steps"]["payment_setup"] = stripe_product
        # Step 3: Generate marketing copy
        if self.llm.enabled:
            marketing = await self.llm.generate_marketing_copy(
                f"{opportunity['keyword']} Guide", "entrepreneurs and professionals"
            )
            results["launch_steps"]["marketing_copy"] = marketing
        # Step 4: Create email sequence
        email_sequence = await self.email.create_email_sequence(
            f"{opportunity['keyword']} Guide"
        )
        results["launch_steps"]["email_sequence"] = {
            "emails_created": len(email_sequence),
            "sequence": email_sequence,
        }
        # Step 5: Generate social content
        social_posts = await self.social.generate_social_content(
            f"{opportunity['keyword']} Guide", "twitter"
        )
        results["launch_steps"]["social_content"] = {
            "posts_created": len(social_posts),
            "platforms": ["twitter", "linkedin"],
        }
        # Calculate revenue potential
        if opportunity.get("trend_score", 0) > 0.8:
            results["total_revenue_potential"] = 5000  # High potential
        elif opportunity.get("trend_score", 0) > 0.6:
            results["total_revenue_potential"] = 2000  # Medium potential
        else:
            results["total_revenue_potential"] = 500  # Low potential
        return results

    async def run_affiliate_cycle(self, category: Optional[str] = None) -> Dict[str, Any]:
        offers_result = await self.affiliate.fetch_top_offers(category=category)
        offers = offers_result.get("offers", [])
        tracking_links: List[Dict[str, Any]] = []
        for offer in offers:
            offer_id = str(offer.get("id")) if offer.get("id") else None
            link_result = await self.affiliate.create_tracking_link(offer_id) if offer_id else {"success": False}
            tracking_links.append({"offer": offer, "tracking_result": link_result})
        return {"offers": offers, "tracking_links": tracking_links, "api_enabled": self.affiliate.enabled}

    async def run_dropshipping_cycle(self) -> Dict[str, Any]:
        catalog_result = await self.dropshipping.list_products(limit=25)
        open_orders = await self.dropshipping.fetch_open_orders(limit=10)
        return {"catalog": catalog_result, "open_orders": open_orders, "api_enabled": self.dropshipping.enabled}

    async def run_innovation_cycle(self, context: Dict[str, Any], count: int = 5) -> Dict[str, Any]:
        return await self.innovation.propose_streams(context, count=count)
# Global instance
api_manager = APIIntegrationManager()
if __name__ == "__main__":
    import asyncio
    async def test_integrations():
        status = api_manager.get_integration_status()
        logger.info("Integration Status:")
        logger.info(json.dumps(status, indent=2))
        # Test with sample opportunity
        opportunity = {
            "keyword": "AI productivity tools",
            "trend_score": 0.92,
            "market_size": "$2.1B",
        }
        results = await api_manager.execute_full_product_launch(opportunity)
        logger.info("Full Product Launch Results:")
        logger.info(json.dumps(results, indent=2))
    asyncio.run(test_integrations())


