import smtplib
import os
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv()

def debug_smtp():
    print("--- SMTP DEBUGGER ---")
    
    # 1. Check Env Vars
    server = os.getenv("SMTP_SERVER")
    port = os.getenv("SMTP_PORT")
    email = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    
    print(f"Server: {server}")
    print(f"Port: {port}")
    print(f"Email: {email}")
    # Mask password for safety in logs
    masked_pw = '*' * len(password) if password else 'MISSING'
    print(f"Password: {masked_pw}")
    
    if not all([server, port, email, password]):
        print("ERROR: Missing environment variables.")
        return

    # 2. Try Connection
    try:
        print(f"Connecting to {server}:{port}...")
        smtp = smtplib.SMTP(server, int(port))
        print("CONNECTED.")
        
        print("Starting TLS...")
        smtp.starttls()
        print("TLS STARTED.")
        
        print("Logging in...")
        smtp.login(email, password)
        print("LOGIN SUCCESSFUL!")
        
        smtp.quit()
        print("--- TEST PASSED ---")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"AUTH ERROR: {e}")
        print("HINT: Are you using an App Password? (Not your normal Gmail password)")
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    debug_smtp()
