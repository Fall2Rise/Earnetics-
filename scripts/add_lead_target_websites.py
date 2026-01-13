"""
Add target websites for lead generation scraping
These are websites where we can find potential customers (entrepreneurs, makers, business owners)
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.services.lead_generation_service import LeadGenerationService

# Target websites organized by category
TARGET_WEBSITES = [
    # Indie Hacker & Maker Communities
    {
        "domain": "indiehackers.com",
        "base_url": "https://www.indiehackers.com",
        "target_paths": ["/products", "/makers", "/", "/about"],
        "keywords": ["founder", "maker", "entrepreneur", "startup", "product"],
        "description": "Indie Hackers - Community of bootstrapped founders"
    },
    {
        "domain": "producthunt.com",
        "base_url": "https://www.producthunt.com",
        "target_paths": ["/makers", "/", "/topics"],
        "keywords": ["maker", "founder", "creator", "product"],
        "description": "Product Hunt - Product discovery platform"
    },
    {
        "domain": "makerlog.co",
        "base_url": "https://makerlog.co",
        "target_paths": ["/makers", "/", "/about"],
        "keywords": ["maker", "founder", "indie"],
        "description": "Makerlog - Public maker journey tracking"
    },
    
    # Business & Startup Directories
    {
        "domain": "crunchbase.com",
        "base_url": "https://www.crunchbase.com",
        "target_paths": ["/discover/organization/people", "/", "/about"],
        "keywords": ["founder", "CEO", "entrepreneur", "startup"],
        "description": "Crunchbase - Startup and company database"
    },
    {
        "domain": "angel.co",
        "base_url": "https://angel.co",
        "target_paths": ["/people", "/", "/about"],
        "keywords": ["founder", "entrepreneur", "startup"],
        "description": "AngelList - Startup and investor network"
    },
    {
        "domain": "startupbase.io",
        "base_url": "https://startupbase.io",
        "target_paths": ["/founders", "/", "/about"],
        "keywords": ["founder", "startup", "entrepreneur"],
        "description": "StartupBase - Startup directory"
    },
    
    # SaaS & Product Directories
    {
        "domain": "saasdirectory.com",
        "base_url": "https://www.saasdirectory.com",
        "target_paths": ["/companies", "/", "/contact"],
        "keywords": ["SaaS", "founder", "company"],
        "description": "SaaS Directory - SaaS company listings"
    },
    {
        "domain": "getapp.com",
        "base_url": "https://www.getapp.com",
        "target_paths": ["/software", "/", "/about"],
        "keywords": ["software", "business", "company"],
        "description": "GetApp - Software directory"
    },
    {
        "domain": "capterra.com",
        "base_url": "https://www.capterra.com",
        "target_paths": ["/software", "/", "/about"],
        "keywords": ["software", "business", "company"],
        "description": "Capterra - Software directory"
    },
    
    # Creator & Content Platforms
    {
        "domain": "gumroad.com",
        "base_url": "https://gumroad.com",
        "target_paths": ["/discover", "/", "/about"],
        "keywords": ["creator", "maker", "seller"],
        "description": "Gumroad - Creator commerce platform"
    },
    {
        "domain": "creators.tech",
        "base_url": "https://creators.tech",
        "target_paths": ["/creators", "/", "/about"],
        "keywords": ["creator", "maker", "entrepreneur"],
        "description": "Creators Tech - Creator directory"
    },
    
    # Business Forums & Communities
    {
        "domain": "reddit.com",
        "base_url": "https://www.reddit.com",
        "target_paths": ["/r/entrepreneur", "/r/startups", "/r/SaaS", "/r/indiebiz"],
        "keywords": ["entrepreneur", "startup", "founder"],
        "description": "Reddit - Business and entrepreneur communities"
    },
    {
        "domain": "discord.com",
        "base_url": "https://discord.com",
        "target_paths": ["/servers", "/", "/about"],
        "keywords": ["community", "server"],
        "description": "Discord - Community platform (limited scraping)"
    },
    
    # Professional Networks
    {
        "domain": "linkedin.com",
        "base_url": "https://www.linkedin.com",
        "target_paths": ["/company", "/", "/about"],
        "keywords": ["founder", "CEO", "entrepreneur"],
        "description": "LinkedIn - Professional network (limited scraping)"
    },
    
    # Niche Communities
    {
        "domain": "nomadlist.com",
        "base_url": "https://nomadlist.com",
        "target_paths": ["/people", "/", "/about"],
        "keywords": ["digital nomad", "remote worker", "entrepreneur"],
        "description": "Nomad List - Digital nomad community"
    },
    {
        "domain": "remoteok.com",
        "base_url": "https://remoteok.com",
        "target_paths": ["/", "/about"],
        "keywords": ["remote worker", "entrepreneur"],
        "description": "Remote OK - Remote work platform"
    },
    
    # Business Directories
    {
        "domain": "clutch.co",
        "base_url": "https://clutch.co",
        "target_paths": ["/companies", "/", "/about"],
        "keywords": ["company", "business", "service"],
        "description": "Clutch - B2B service provider directory"
    },
    {
        "domain": "goodfirms.co",
        "base_url": "https://www.goodfirms.co",
        "target_paths": ["/companies", "/", "/about"],
        "keywords": ["company", "business", "service"],
        "description": "GoodFirms - B2B service directory"
    },
    
    # Startup Resources
    {
        "domain": "startupgrind.com",
        "base_url": "https://www.startupgrind.com",
        "target_paths": ["/events", "/", "/about"],
        "keywords": ["startup", "entrepreneur", "founder"],
        "description": "Startup Grind - Startup community"
    },
    {
        "domain": "foundersnetwork.com",
        "base_url": "https://foundersnetwork.com",
        "target_paths": ["/members", "/", "/about"],
        "keywords": ["founder", "startup", "entrepreneur"],
        "description": "Founders Network - Founder community"
    },
    
    # Tech & Innovation
    {
        "domain": "techstars.com",
        "base_url": "https://www.techstars.com",
        "target_paths": ["/companies", "/", "/about"],
        "keywords": ["startup", "founder", "entrepreneur"],
        "description": "Techstars - Startup accelerator"
    },
    {
        "domain": "ycombinator.com",
        "base_url": "https://www.ycombinator.com",
        "target_paths": ["/companies", "/", "/about"],
        "keywords": ["startup", "founder", "YC"],
        "description": "Y Combinator - Startup accelerator"
    },
    
    # E-commerce & Dropshipping
    {
        "domain": "oberlo.com",
        "base_url": "https://www.oberlo.com",
        "target_paths": ["/blog", "/", "/about"],
        "keywords": ["dropshipping", "ecommerce", "entrepreneur"],
        "description": "Oberlo - Dropshipping platform"
    },
    {
        "domain": "shopify.com",
        "base_url": "https://www.shopify.com",
        "target_paths": ["/partners", "/", "/about"],
        "keywords": ["ecommerce", "merchant", "entrepreneur"],
        "description": "Shopify - E-commerce platform"
    },
    
    # Freelancer & Agency Platforms
    {
        "domain": "clutch.co",
        "base_url": "https://clutch.co",
        "target_paths": ["/agencies", "/", "/about"],
        "keywords": ["agency", "service provider", "business"],
        "description": "Clutch - Agency directory"
    },
    {
        "domain": "upwork.com",
        "base_url": "https://www.upwork.com",
        "target_paths": ["/agencies", "/", "/about"],
        "keywords": ["freelancer", "agency", "service"],
        "description": "Upwork - Freelance platform"
    },
    
    # Additional High-Value Targets
    {
        "domain": "betatesters.com",
        "base_url": "https://betatesters.com",
        "target_paths": ["/", "/about"],
        "keywords": ["founder", "startup", "product"],
        "description": "Beta Testers - Product testing community"
    },
    {
        "domain": "betalist.com",
        "base_url": "https://betalist.com",
        "target_paths": ["/startups", "/", "/about"],
        "keywords": ["startup", "founder", "product"],
        "description": "BetaList - Startup launch platform"
    },
    {
        "domain": "hackernews.com",
        "base_url": "https://news.ycombinator.com",
        "target_paths": ["/", "/show", "/ask"],
        "keywords": ["founder", "startup", "entrepreneur"],
        "description": "Hacker News - Tech community"
    },
    {
        "domain": "dev.to",
        "base_url": "https://dev.to",
        "target_paths": ["/", "/top/week"],
        "keywords": ["developer", "founder", "startup"],
        "description": "DEV Community - Developer platform"
    },
    {
        "domain": "medium.com",
        "base_url": "https://medium.com",
        "target_paths": ["/tag/entrepreneurship", "/tag/startups", "/"],
        "keywords": ["founder", "entrepreneur", "startup"],
        "description": "Medium - Content platform with entrepreneurs"
    },
    {
        "domain": "substack.com",
        "base_url": "https://substack.com",
        "target_paths": ["/directory", "/", "/about"],
        "keywords": ["creator", "writer", "entrepreneur"],
        "description": "Substack - Newsletter platform"
    },
    {
        "domain": "ghost.org",
        "base_url": "https://ghost.org",
        "target_paths": ["/customers", "/", "/about"],
        "keywords": ["publisher", "creator", "entrepreneur"],
        "description": "Ghost - Publishing platform"
    },
    {
        "domain": "notion.so",
        "base_url": "https://www.notion.so",
        "target_paths": ["/", "/templates"],
        "keywords": ["creator", "business", "productivity"],
        "description": "Notion - Productivity platform"
    },
    {
        "domain": "airtable.com",
        "base_url": "https://airtable.com",
        "target_paths": ["/templates", "/", "/about"],
        "keywords": ["business", "creator", "entrepreneur"],
        "description": "Airtable - Database platform"
    },
    {
        "domain": "zapier.com",
        "base_url": "https://zapier.com",
        "target_paths": ["/apps", "/", "/about"],
        "keywords": ["automation", "business", "entrepreneur"],
        "description": "Zapier - Automation platform"
    },
    {
        "domain": "make.com",
        "base_url": "https://www.make.com",
        "target_paths": ["/scenarios", "/", "/about"],
        "keywords": ["automation", "business", "entrepreneur"],
        "description": "Make - Automation platform"
    },
    {
        "domain": "bubble.io",
        "base_url": "https://bubble.io",
        "target_paths": ["/showcase", "/", "/about"],
        "keywords": ["founder", "maker", "startup"],
        "description": "Bubble - No-code platform"
    },
    {
        "domain": "webflow.com",
        "base_url": "https://webflow.com",
        "target_paths": ["/showcase", "/", "/about"],
        "keywords": ["designer", "founder", "creator"],
        "description": "Webflow - No-code platform"
    },
    {
        "domain": "figma.com",
        "base_url": "https://www.figma.com",
        "target_paths": ["/community", "/", "/about"],
        "keywords": ["designer", "founder", "creator"],
        "description": "Figma - Design platform"
    },
    {
        "domain": "dribbble.com",
        "base_url": "https://dribbble.com",
        "target_paths": ["/designers", "/", "/about"],
        "keywords": ["designer", "freelancer", "creator"],
        "description": "Dribbble - Design community"
    },
    {
        "domain": "behance.net",
        "base_url": "https://www.behance.net",
        "target_paths": ["/", "/search"],
        "keywords": ["designer", "creator", "freelancer"],
        "description": "Behance - Creative portfolio platform"
    },
    {
        "domain": "fiverr.com",
        "base_url": "https://www.fiverr.com",
        "target_paths": ["/sellers", "/", "/about"],
        "keywords": ["freelancer", "seller", "entrepreneur"],
        "description": "Fiverr - Freelance marketplace"
    },
    {
        "domain": "99designs.com",
        "base_url": "https://99designs.com",
        "target_paths": ["/designers", "/", "/about"],
        "keywords": ["designer", "freelancer", "creator"],
        "description": "99designs - Design marketplace"
    },
    {
        "domain": "toptal.com",
        "base_url": "https://www.toptal.com",
        "target_paths": ["/", "/about"],
        "keywords": ["freelancer", "developer", "entrepreneur"],
        "description": "Toptal - Elite freelancer network"
    },
    {
        "domain": "freelancer.com",
        "base_url": "https://www.freelancer.com",
        "target_paths": ["/", "/about"],
        "keywords": ["freelancer", "entrepreneur"],
        "description": "Freelancer - Freelance marketplace"
    },
    {
        "domain": "indeed.com",
        "base_url": "https://www.indeed.com",
        "target_paths": ["/companies", "/", "/about"],
        "keywords": ["employer", "business", "company"],
        "description": "Indeed - Job platform"
    },
    {
        "domain": "glassdoor.com",
        "base_url": "https://www.glassdoor.com",
        "target_paths": ["/Overview", "/", "/about"],
        "keywords": ["employer", "company", "business"],
        "description": "Glassdoor - Company reviews"
    },
]

def add_all_target_websites():
    """Add all target websites to the lead generation system"""
    lead_service = LeadGenerationService()
    
    added_count = 0
    updated_count = 0
    errors = []
    
    print("Adding target websites for lead generation...")
    print(f"Total websites to add: {len(TARGET_WEBSITES)}\n")
    
    for site in TARGET_WEBSITES:
        try:
            result = lead_service.add_target_website(
                domain=site["domain"],
                base_url=site["base_url"],
                target_paths=site.get("target_paths", []),
                keywords=site.get("keywords", [])
            )
            
            if result.get("status") == "added":
                added_count += 1
                print(f"[+] Added: {site['domain']} - {site.get('description', '')}")
            elif result.get("status") == "updated":
                updated_count += 1
                print(f"[~] Updated: {site['domain']} - {site.get('description', '')}")
        except Exception as e:
            errors.append((site["domain"], str(e)))
            print(f"[X] Error adding {site['domain']}: {e}")
    
    print(f"\nSummary:")
    print(f"  Added: {added_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Errors: {len(errors)}")
    
    if errors:
        print(f"\nErrors encountered:")
        for domain, error in errors:
            print(f"  - {domain}: {error}")
    
    # Show current target websites
    print(f"\nCurrent target websites in system:")
    current_sites = lead_service.get_target_websites(enabled_only=False)
    for site in current_sites[:10]:  # Show first 10
        status = "Enabled" if site.get("enabled") else "Disabled"
        print(f"  - {site['domain']} - {status}")
    
    if len(current_sites) > 10:
        print(f"  ... and {len(current_sites) - 10} more")
    
    return {
        "added": added_count,
        "updated": updated_count,
        "errors": len(errors),
        "total": len(current_sites)
    }

if __name__ == "__main__":
    result = add_all_target_websites()
    print(f"\nDone! {result['total']} target websites configured for lead generation.")
