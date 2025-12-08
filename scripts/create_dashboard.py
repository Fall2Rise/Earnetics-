"""Create command center HTML file."""

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Revenue Command Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.2em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h2 { color: #667eea; margin-bottom: 15px; font-size: 1.5em; }
        .status { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; }
        .status-dot.green { background: #10b981; }
        .status-dot.red { background: #ef4444; }
        .status-dot.yellow { background: #f59e0b; }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: background 0.3s;
        }
        .btn:hover { background: #764ba2; }
        .links { display: flex; gap: 10px; flex-wrap: wrap; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Revenue Command Center</h1>
            <p class="subtitle">Your autonomous revenue generation system is online</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>System Status</h2>
                <div class="status"><div class="status-dot green"></div><span>Server Running</span></div>
                <div class="status"><div class="status-dot green"></div><span>30 AI Agents Active</span></div>
                <div class="status"><div class="status-dot green"></div><span>Database Connected</span></div>
                <div class="status"><div class="status-dot yellow"></div><span>Stripe Key Needs Update</span></div>
            </div>

            <div class="card">
                <h2>Quick Actions</h2>
                <button class="btn" onclick="window.location.href='/docs'">📚 API Documentation</button>
                <button class="btn" onclick="window.location.href='/api/guardian/health'">🔐 Check API Keys</button>
                <button class="btn" onclick="window.location.href='/health'">❤️ Health Check</button>
            </div>

            <div class="card">
                <h2>Revenue Streams</h2>
                <p>🎯 Automation Mastermind - $497</p>
                <p>🤖 24/7 AI Sales Agent - $297</p>
                <p>🎨 AI Content Engine - $197</p>
                <p>📦 Automation Vault - $97</p>
            </div>
        </div>

        <div class="card">
            <h2>🔗 Important Links</h2>
            <div class="links">
                <button class="btn" onclick="window.location.href='/docs'">Interactive API Docs</button>
                <button class="btn" onclick="window.location.href='/redoc'">API Schema</button>
                <button class="btn" onclick="window.location.href='/api/system/status'">System Metrics</button>
                <button class="btn" onclick="window.location.href='/api/stripe/products'">Stripe Products</button>
                <button class="btn" onclick="window.location.href='/api/campaigns'">Email Campaigns</button>
                <button class="btn" onclick="window.location.href='/api/content/status'">Content Engine</button>
            </div>
        </div>

        <div class="card">
            <h2>⚠️ Action Required</h2>
            <p style="color: #ef4444; margin-bottom: 15px;">
                <strong>Stripe API Key Expired</strong><br>
                Your Stripe key needs to be updated for payment processing to work.
            </p>
            <ol style="margin-left: 20px; line-height: 1.8;">
                <li>Go to <a href="https://dashboard.stripe.com/apikeys" target="_blank">Stripe Dashboard</a></li>
                <li>Copy your Live Secret Key (starts with sk_live_)</li>
                <li>Update the STRIPE_SECRET_KEY in your .env file</li>
                <li>Restart the server</li>
            </ol>
        </div>
    </div>

    <script>
        setInterval(() => {
            fetch('/health')
                .then(r => r.json())
                .then(data => console.log('Health check:', data))
                .catch(e => console.error('Health check failed:', e));
        }, 30000);
    </script>
</body>
</html>'''

with open('command_center.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Command center HTML created successfully!")
