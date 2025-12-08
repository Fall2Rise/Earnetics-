import requests
import json
import sys
import os
from datetime import datetime

BASE_URL = "http://localhost:8080"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*60)
    print("   🚀 AI REVENUE COMMAND CENTER - LAUNCHPAD")
    print("="*60)

def check_health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        if r.status_code == 200:
            print("✅ System Status: ONLINE")
            print(f"   Agents: {r.json().get('active_agents', 'Unknown')}")
        else:
            print("❌ System Status: OFFLINE or ERROR")
    except:
        print("❌ System Status: UNREACHABLE (Is server running?)")

def send_campaign():
    print("\n📧 LAUNCH EMAIL CAMPAIGN")
    print("-" * 30)
    print("Tip: Leave Subject/Body empty to AUTO-GENERATE content using AI.")
    
    subject = input("Subject: ").strip()
    body = ""
    
    if not subject:
        print("\n🤖 Auto-generating email content...")
        try:
            # Request content generation from the API
            # Endpoint: /api/content-engine/generate
            # Payload: {"topic": "...", "tone": "viral"}
            gen_payload = {"topic": "AI Automation Launch", "tone": "professional"}
            r = requests.post(f"{BASE_URL}/api/content-engine/generate", json=gen_payload, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                content = data.get('content', '')
                
                # Parse the master content
                # The mock returns "Master Content for: ..."
                lines = content.split('\n', 1)
                subject = lines[0].replace('Master Content for:', 'Subject:').strip()
                body = lines[1].strip() if len(lines) > 1 else content
                
                print(f"   > Generated Subject: {subject}")
            else:
                print(f"   ❌ Failed to auto-generate (Status {r.status_code}). Using defaults.")
                subject = "Unlock the Power of AI"
                body = "Discover how our AI agents can scale your business."
        except Exception as e:
            print(f"   ❌ Error generating content: {e}")
            subject = "Unlock the Power of AI"
            body = "Discover how our AI agents can scale your business."

    if not body:
        body = input("Body: ").strip()

    recipient = input("Test Recipient Email: ")
    
    payload = {
        "subject": subject,
        "body": body,
        "recipients": [recipient]
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/campaigns/email", json=payload, timeout=5)
        if r.status_code == 200:
            print(f"\n✅ Campaign Sent! ID: {r.json().get('campaign_id')}")
        else:
            print(f"\n❌ Failed: {r.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def generate_content():
    print("\n🎨 GENERATE SOCIAL CONTENT")
    print("-" * 30)
    topic = input("Topic (e.g., 'AI Automation'): ")
    platform = input("Platform (twitter/linkedin): ")
    
    payload = {
        "topic": topic,
        "platform": platform
    }
    
    try:
        print("\n🤖 Generating content... (this may take a moment)")
        # Assuming content engine endpoint exists from previous implementation
        # If not, this is a placeholder for where it would go
        r = requests.post(f"{BASE_URL}/api/content/generate", json=payload)
        if r.status_code == 200:
            print("\n✅ Content Generated:")
            print("-" * 20)
            print(r.json().get('content', 'No content returned'))
            print("-" * 20)
        else:
            print(f"\n❌ Failed: {r.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    while True:
        clear_screen()
        print_header()
        check_health()
        print("\nOPERATIONAL MENU:")
        print("1. 📧 Launch Email Campaign")
        print("2. 🎨 Generate Social Content")
        print("3. 🔐 Check API Keys (Guardian)")
        print("4. 💰 Create New Revenue Stream")
        print("5. 🤖 Start Autonomous Agents")
        print("6. 🚪 Exit")
        print("7. 💾 Seed Database (Fill Command Center)")
        
        choice = input("\nSelect an option (1-7): ")
        
        if choice == '1':
            send_campaign()
            input("\nPress Enter to continue...")
        elif choice == '2':
            generate_content()
            input("\nPress Enter to continue...")
        elif choice == '3':
            try:
                r = requests.get(f"{BASE_URL}/api/guardian/health")
                print(json.dumps(r.json(), indent=2))
            except:
                print("Failed to contact Guardian.")
            input("\nPress Enter to continue...")
        elif choice == '4':
            os.system(f"python {os.path.join('scripts', 'create_custom_revenue_stream.py')}")
            input("\nPress Enter to continue...")
        elif choice == '5':
            print("\n🤖 STARTING AUTONOMOUS AGENTS...")
            print("To stop, press Ctrl+C")
            print("-" * 30)
            # Using the batch file or direct python call depending on what's available
            # Assuming we want to run the agent simulation
            try:
                os.system("python ai_corporation_agents.py")
            except KeyboardInterrupt:
                print("\n🛑 Agents Stopped.")
            input("\nPress Enter to continue...")
        elif choice == '6':
            print("Exiting...")
            sys.exit(0)
        elif choice == '7':
            os.system(f"python {os.path.join('scripts', 'seed_command_center.py')}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
