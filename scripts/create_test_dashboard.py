"""Create a guaranteed-working minimal dashboard."""

html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Revenue Command Center - Loading...</title>
</head>
<body>
    <h1>AI Revenue Command Center</h1>
    <p>If you see this, the server is working!</p>
    <p>Checking system status...</p>
    <div id="status"></div>
    <script>
        fetch('/health')
            .then(r => r.json())
            .then(data => {
                document.getElementById('status').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(e => {
                document.getElementById('status').innerHTML = '<p style="color:red">Error: ' + e + '</p>';
            });
    </script>
</body>
</html>"""

with open('test_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Created test_dashboard.html")
