"""Create final working dashboard."""

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Revenue Command Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h2 { color: #667eea; margin-bottom: 15px; }
        .status { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10b981;
        }
        .dot.yellow { background: #f59e0b; }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px 5px 5px 0;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #764ba2; }
        .warning {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin-top: 20px;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Revenue Command Center</h1>
            <p class="subtitle">Autonomous Revenue Generation System - Online</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>System Status</h2>
                <div class="status"><div class="dot"></div><span>Server Running</span></div>
                <div class="status"><div class="dot"></div><span>30 AI Agents Active</span></div>
                <div class="status"><div class="dot"></div><span>Email System Ready</span></div>
                <div class="status"><div class="dot yellow"></div><span>Stripe Key Expired</span></div>
            </div>

            <div class="card">
                <h2>Quick Actions</h2>
                <a href="/docs" class="btn">📚 API Documentation</a>
                <a href="/health" class="btn">❤️ Health Check</a>
                <a href="/api/guardian/health" class="btn">🔐 API Key Status</a>
                <a href="/api/system/status" class="btn">📊 System Metrics</a>
            </div>

            <div class="card">
                <h2>Revenue Streams</h2>
                <p>🎯 Automation Mastermind - $497</p>
                <p>🤖 24/7 AI Sales Agent - $297</p>
                <p>🎨 AI Content Engine - $197</p>
                <p>📦 Automation Vault - $97</p>
            </div>
        </div>

        <div class="card warning">
            <h3 style="color: #f59e0b; margin-bottom: 10px;">⚠️ Action Required</h3>
            <p><strong>Stripe API Key Expired</strong></p>
            <p style="margin-top: 10px;">To enable payment processing:</p>
            <ol style="margin: 10px 0 0 20px; line-height: 1.8;">
                <li>Get new key from <a href="https://dashboard.stripe.com/apikeys" target="_blank">Stripe Dashboard</a></li>
                <li>Update STRIPE_SECRET_KEY in .env file</li>
                <li>Restart server</li>
            </ol>
        </div>
    </div>
</body>
</html>"""

with open('command_center.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Dashboard created successfully!")
