#!/usr/bin/env python3
"""
AUTONOMOUS SYSTEM LAUNCHER (EARNETICS CORE)

Starts all autonomous systems, including financial processing,
and validates that the environment is ready for autonomous operation.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# Ensure backend is importable when this script is run directly
sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "autonomous_system.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("AutonomousLauncher")

# ---------------------------------------------------------------------------
# Imports that rely on path setup
# ---------------------------------------------------------------------------

from autonomous_financial_processor import AutonomousFinancialProcessor  # type: ignore


# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------

def check_environment() -> None:
    """
    Check that required and recommended environment variables are set.

    Design:
    - Only hard requirement for real operations: Stripe secret key.
    - LLM stack is provider-agnostic and optional, but strongly recommended.
    - Email / notification stack is optional.
    """
    logger.info("🔍 Checking environment configuration...")
    logger.info(f"📂 Project root: {PROJECT_ROOT}")
    logger.info(f"🗂️  Logs directory: {LOG_DIR}")

    # Required for any real payment processing
    required_vars = {
        "STRIPE_SECRET_KEY": "Stripe API key for payment processing",
    }

    # LLM stack: generic, supports local and remote providers
    llm_vars = {
        "LLM_PROVIDER": "Primary LLM provider identifier (e.g. 'ollama', 'openrouter', 'grok', 'google', 'anthropic')",
        "LLM_MODEL": "Default LLM model name (used if provider supports it)",
        "OLLAMA_MODEL": "Local model name for Ollama provider (e.g. 'llama3.1:8b')",
        "OLLAMA_BASE_URL": "Base URL for local model server (e.g. 'http://localhost:11434')",
        "OPENROUTER_API_KEY": "API key for OpenRouter routing",
        "GROK_API_KEY": "API key for Grok provider",
        "GOOGLE_API_KEY": "API key for Google Generative API",
        "ANTHROPIC_API_KEY": "API key for Anthropic models",
    }

    # Optional but useful infrastructure pieces
    optional_vars = {
        "STRIPE_WEBHOOK_SECRET": "Stripe webhook secret for event handling",
        "SMTP_HOST": "Email server host for notifications",
        "SMTP_PORT": "Email server port",
        "SMTP_USER": "Email username",
        "SMTP_PASSWORD": "Email password",
        "EARNETICS_ENV": "Environment name (e.g. 'dev', 'staging', 'prod')",
    }

    missing_required: list[str] = []
    missing_optional: list[str] = []
    llm_present_detail: list[str] = []

    # Required
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"  ❌ {var}: {description}")
        else:
            logger.info(f"  ✅ {var} configured")

    # LLM stack (soft requirement, but critical for full autonomy)
    for var, description in llm_vars.items():
        value = os.getenv(var)
        if value:
            llm_present_detail.append(f"  ✅ {var} = {value}")
        else:
            # We don't treat these as errors; we just note them in aggregate
            continue

    # Optional
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"  ⚠️  {var}: {description}")
        else:
            logger.info(f"  ✅ {var} configured")

    # Stripe requirements
    if missing_required:
        logger.error("\n❌ MISSING REQUIRED CONFIGURATION FOR LIVE OPERATIONS:")
        for msg in missing_required:
            logger.error(msg)
        logger.error(
            "\nWithout these, real payment processing will NOT function correctly.\n"
            "You can create a .env file in the project root containing, for example:\n\n"
            "STRIPE_SECRET_KEY=sk_live_your_key_here\n"
        )
        logger.info("⚠️ System will still start, but financial features will be disabled or simulated.\n")

    # LLM summary
    if llm_present_detail:
        logger.info("\n🤖 LLM STACK DETECTED:")
        for line in llm_present_detail:
            logger.info(line)
    else:
        logger.warning(
            "\n⚠️  No LLM provider configuration detected.\n"
            "    Earnetics will run in LIMITED MODE (no autonomous AI reasoning/content).\n"
            "    To enable full autonomy, set something like:\n\n"
            "    LLM_PROVIDER=ollama\n"
            "    OLLAMA_MODEL=llama3.1:8b\n"
            "    OLLAMA_BASE_URL=http://localhost:11434\n"
        )

    # Optional pieces
    if missing_optional:
        logger.warning("\n⚠️  OPTIONAL CONFIGURATION NOT SET:")
        for msg in missing_optional:
            logger.warning(msg)
        logger.warning("These features will be limited until configured (emails, webhooks, environment labels).\n")

    logger.info("✅ Environment check complete.\n")


# ---------------------------------------------------------------------------
# System orchestration
# ---------------------------------------------------------------------------

async def start_all_systems() -> None:
    """
    Start all autonomous systems.

    Currently:
    - Runs the autonomous financial processor.
    - In future, this is where additional Earnetics subsystems get orchestrated.
    """
    logger.info("=" * 80)
    logger.info("🚀 LAUNCHING EARNETICS AUTONOMOUS AI BUSINESS SYSTEM")
    logger.info("=" * 80)

    # Verify environment and log capabilities
    check_environment()

    # Initialize systems
    logger.info("🧠 Initializing autonomous financial processor...")
    financial_processor = AutonomousFinancialProcessor()

    logger.info("✅ All systems initialized")
    logger.info("🤖 Autonomous operation beginning...")
    logger.info("=" * 80)

    try:
        await financial_processor.start_autonomous_processing()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown signal received")
        try:
            financial_processor.stop()
        except Exception as stop_err:  # pragma: no cover
            logger.error(f"Error during financial_processor.stop(): {stop_err}", exc_info=True)
        logger.info("✅ All systems stopped gracefully")
    except Exception as e:
        logger.error(f"❌ Unhandled error in autonomous systems: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(start_all_systems())
    except Exception as e:
        logger.error(f"❌ Fatal error in launcher: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
