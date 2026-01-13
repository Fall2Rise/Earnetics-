"""
Website Growth & Digital Presence API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from backend.services.website_growth_service import WebsiteGrowthService
from backend.services.community_service import CommunityService
from backend.services.product_delivery_service import ProductDeliveryService
from backend.middleware.rate_limiter import rate_limit

router = APIRouter(prefix="/api/website-growth", tags=["website-growth"])

@router.get("/websites")
def list_websites(
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get all managed websites"""
    service = WebsiteGrowthService()
    websites = service.get_websites()
    return {"websites": websites, "total": len(websites)}

@router.post("/websites")
def add_website(
    domain: str,
    url: str,
    purpose: str = "",
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Add a new website to manage"""
    service = WebsiteGrowthService()
    result = service.add_website(domain, url, purpose)
    return result

@router.get("/websites/{website_id}/blog-posts")
def get_blog_posts(
    website_id: int,
    status: Optional[str] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get blog posts for a website"""
    service = WebsiteGrowthService()
    posts = service.get_blog_posts(website_id=website_id, status=status)
    return {"posts": posts, "total": len(posts)}

@router.post("/websites/{website_id}/blog-posts")
def create_blog_post(
    website_id: int,
    title: str,
    content: str,
    author: str = "AI Content Writer",
    category: str = "General",
    tags: Optional[List[str]] = None,
    seo_keywords: Optional[List[str]] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Create a new blog post"""
    service = WebsiteGrowthService()
    result = service.create_blog_post(
        website_id=website_id,
        title=title,
        content=content,
        author=author,
        category=category,
        tags=tags or [],
        seo_keywords=seo_keywords or []
    )
    return result

@router.post("/blog-posts/{post_id}/publish")
def publish_blog_post(
    post_id: int,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Publish a blog post"""
    service = WebsiteGrowthService()
    result = service.publish_blog_post(post_id)
    return result

@router.get("/websites/{website_id}/social-connections")
def get_social_connections(
    website_id: int,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get social media connections for a website"""
    service = WebsiteGrowthService()
    connections = service.get_social_connections(website_id=website_id)
    return {"connections": connections, "total": len(connections)}

@router.post("/websites/{website_id}/social-connections")
def connect_social_account(
    website_id: int,
    platform: str,
    account_handle: str,
    access_token: Optional[str] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Connect a social media account to a website"""
    service = WebsiteGrowthService()
    result = service.connect_social_account(website_id, platform, account_handle, access_token)
    return result

@router.get("/websites/{website_id}/affiliate-links")
def get_affiliate_links(
    website_id: int,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get affiliate links for a website"""
    service = WebsiteGrowthService()
    links = service.get_affiliate_links(website_id=website_id)
    return {"links": links, "total": len(links)}

@router.get("/websites/{website_id}/analytics")
def get_website_analytics(
    website_id: int,
    days: int = 30,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get website analytics"""
    service = WebsiteGrowthService()
    analytics = service.get_analytics(website_id=website_id, days=days)
    return {"analytics": analytics, "total_days": len(analytics)}

@router.get("/community/platforms")
def get_community_platforms(
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get all community platforms"""
    service = CommunityService()
    platforms = service.get_platforms()
    return {"platforms": platforms, "total": len(platforms)}

@router.get("/community/members")
def get_community_members(
    platform_type: Optional[str] = None,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Get community members"""
    service = CommunityService()
    members = service.get_members(platform_type=platform_type)
    return {"members": members, "total": len(members)}

@router.get("/products/{product_id}/delivery-verify")
def verify_product_delivery(
    product_id: int,
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    """Verify a product has deliverable content"""
    service = ProductDeliveryService()
    result = service.verify_product_has_content(product_id)
    return result
