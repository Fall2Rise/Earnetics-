import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

# Load env vars
load_dotenv(override=True)

from ai_corporation_agents import AIRevenueCorporation

async def generate_emails():
    print("--- 📧 GENERATING EMAIL LAUNCH SEQUENCE ---")
    corp = AIRevenueCorporation()
    
    marketing_agent = corp.agents["marketing_manager"]
    
    context = {
        "product": "Automation Mastermind",
        "price": 497,
        "target_audience": "Business Owners",
        "goal": "Convert leads to high-ticket sales",
        "sequence_length": 5
    }
    
    print("Thinking...")
    # We ask the agent to write the actual emails
    thought = marketing_agent.think(
        "Write a 5-email launch sequence for the Automation Mastermind. "
        "Include subject lines and body copy for each email. "
        "Email 1: Value/Problem Agitation. "
        "Email 2: The Solution (Automation). "
        "Email 3: Social Proof/Case Study. "
        "Email 4: The Offer (Mastermind). "
        "Email 5: Urgency/Closing.", 
        context
    )
    
    print("\n>>> EMAIL SEQUENCE GENERATED:\n")
    print(thought.get("marketing_strategy", "No strategy returned"))
    
    # Save to file
    with open("email_sequence.md", "w", encoding="utf-8") as f:
        f.write("# Automation Mastermind - Launch Sequence\n\n")
        f.write(str(thought.get("marketing_strategy", "No content")))

if __name__ == "__main__":
    asyncio.run(generate_emails())
