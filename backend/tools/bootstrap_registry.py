# backend/tools/bootstrap_registry.py
from __future__ import annotations

from typing import Any, Dict

from backend.tools.tool_registry import ToolRegistry, ToolSpec
from backend.tools.handlers.stripe_tools import (
    stripe_get_account,
    stripe_get_recent_payments,
    stripe_create_product,
)
from backend.tools.handlers.scrape_tools import (
    web_scrape_url,
    scrape_website,
)


# Example tool handlers (replace/expand with your real ones)
def healthcheck_tool(_: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "service": "earn-unified-backend"}


def bootstrap_tools(registry: ToolRegistry) -> ToolRegistry:
    """
    Single source of truth for tool registration.
    Map each tool to a governance category.
    """

    # SAFE categories (usually allowed even in SAFE_AUTONOMY)
    registry.register(
        ToolSpec(
            name="healthcheck",
            category="READ_ONLY",
            handler=healthcheck_tool,
            description="Basic backend healthcheck."
        )
    )

    # Stripe tools
    registry.register(
        ToolSpec(
            name="stripe.get_account",
            category="READ_ONLY",  # Safe read operation
            handler=stripe_get_account,
            description="Retrieve Stripe account diagnostics (read-only)."
        )
    )

    registry.register(
        ToolSpec(
            name="stripe.get_recent_payments",
            category="READ_ONLY",  # Safe read operation
            handler=stripe_get_recent_payments,
            description="Get recent Stripe payments/charges (read-only)."
        )
    )

    registry.register(
        ToolSpec(
            name="stripe.create_product",
            category="PAYMENTS",  # Requires approval in SAFE_AUTONOMY
            handler=stripe_create_product,
            description="Create a Stripe product and price."
        )
    )

    # Scraping tools
    registry.register(
        ToolSpec(
            name="scrape.url",
            category="SCRAPE",  # Requires approval in SAFE_AUTONOMY
            handler=web_scrape_url,
            description="Fetch a URL and return page text."
        )
    )

    registry.register(
        ToolSpec(
            name="scrape.website",
            category="SCRAPE",  # Requires approval in SAFE_AUTONOMY
            handler=scrape_website,
            description="Scrape a website domain (multiple pages)."
        )
    )

    # Placeholders — register your real tool handlers here.
    # Categories should match governance policies you already set in backend/core/governance.py
    # Examples:
    # - READ_ONLY: filesystem.read, network.read, payments.read
    # - WRITE_LOCAL: filesystem.write, database.write
    # - PUBLISH: content.publish, page.publish
    # - OUTREACH: email.send, dm.send
    # - PAYMENTS: stripe.create_product, stripe.process_payment
    # - SCRAPE: scraping.collect_leads, scraping.collect_data
    # - EXEC_SYSTEM: system.run_command, system.execute_script

    # TODO: Import your real tool handlers and register them:
    # Example registrations (uncomment and implement as needed):
    #
    # from backend.tools.stripe_tools import stripe_sync_products, stripe_create_product
    # registry.register("stripe_sync_products", "READ_ONLY", stripe_sync_products)
    # registry.register("stripe_create_product", "PAYMENTS", stripe_create_product)
    #
    # from backend.tools.content_tools import publish_blog_post, publish_page
    # registry.register("publish_blog_post", "PUBLISH", publish_blog_post)
    # registry.register("publish_page", "PUBLISH", publish_page)
    #
    # from backend.tools.outreach_tools import send_email, send_dm
    # registry.register("send_email", "OUTREACH", send_email)
    # registry.register("send_dm", "OUTREACH", send_dm)
    #
    # from backend.tools.scrape_tools import scrape_leads, collect_data
    # registry.register("scrape_leads", "SCRAPE", scrape_leads)
    # registry.register("collect_data", "SCRAPE", collect_data)
    #
    # from backend.tools.system_tools import run_command, execute_script
    # registry.register("run_command", "EXEC_SYSTEM", run_command)
    # registry.register("execute_script", "EXEC_SYSTEM", execute_script)
    #
    # from backend.tools.local_tools import save_file, update_database
    # registry.register("save_file", "WRITE_LOCAL", save_file)
    # registry.register("update_database", "WRITE_LOCAL", update_database)

    return registry
