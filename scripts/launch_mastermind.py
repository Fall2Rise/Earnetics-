import asyncio
import os
import sys
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from ai_corporation_agents import AIRevenueCorporation

async def launch_mastermind():
    print("--- 🚀 INITIALIZING AUTOMATION MASTERMIND LAUNCH ---")
    corp = AIRevenueCorporation()
    
    # 1. Product Manager: Create the Product Asset
    print("\n[1/3] 🧠 Product Manager (Aurora) is defining the offer...")
    product_context = {
        "product_name": "Automation Mastermind",
        "price": 497,
        "type": "high_ticket_course",
        "target_audience": "Business Owners"
    }
    # Simulating the agent thinking process
    product_agent = corp.agents["product_manager"]
    product_thought = product_agent.think("Define core value proposition and modules for Automation Mastermind", product_context)
    
    print(f"\n>>> PRODUCT STRATEGY:\n{product_thought['product_strategy']}")
    print(f">>> KEY FEATURES: {product_thought['feature_prioritization']}")
    print(f">>> PRICING: {product_thought['pricing_strategy']}")

    # 2. Sales Director: Create the Outreach Strategy
    print("\n[2/3] 💼 Sales Director (Mercury) is building the pipeline...")
    sales_context = {
        "product": "Automation Mastermind",
        "price": 497,
        "goal": "10 sales in 30 days"
    }
    sales_agent = corp.agents["sales_director"]
    sales_thought = sales_agent.think("Develop cold outreach strategy for high-ticket sales", sales_context)
    
    print(f"\n>>> DEBUG SALES THOUGHT: {sales_thought}")
    
    print(f"\n>>> SALES STRATEGY:\n{sales_thought.get('sales_strategy', 'N/A')}")
    print(f">>> CLOSING TECH: {sales_thought.get('closing_techniques', 'N/A')}")
    print(f">>> FORECAST: {sales_thought.get('revenue_forecast', 'N/A')}")

    # 3. Marketing Manager: Create the Campaign
    print("\n[3/3] 📣 Marketing Manager (Nova) is drafting the campaign...")
    marketing_context = {
        "product": "Automation Mastermind",
        "channel": "Email"
    }
    marketing_agent = corp.agents["marketing_manager"]
    marketing_thought = marketing_agent.think("Draft email campaign hooks for Mastermind", marketing_context)
    
    print(f"\n>>> MARKETING HOOK:\n{marketing_thought['marketing_strategy']}")
    print(f">>> TARGET AUDIENCE: {marketing_thought['target_audience']}")
    
    print("\n--- ✅ LAUNCH PLAN GENERATED ---")
    
    # Save to a report file
    with open("launch_report.txt", "w") as f:
        f.write("AUTOMATION MASTERMIND LAUNCH PLAN\n=================================\n\n")
        f.write(f"PRODUCT STRATEGY:\n{product_thought['product_strategy']}\n\n")
        f.write(f"SALES STRATEGY:\n{sales_thought['sales_strategy']}\n\n")
        f.write(f"MARKETING STRATEGY:\n{marketing_thought['marketing_strategy']}\n")

if __name__ == "__main__":
    import traceback
    with open("launch_log.txt", "w", encoding="utf-8") as log:
        sys.stdout = log
        sys.stderr = log
        try:
            asyncio.run(launch_mastermind())
        except Exception as e:
            log.write(f"CRITICAL ERROR: {e}\n")
            traceback.print_exc(file=log)
