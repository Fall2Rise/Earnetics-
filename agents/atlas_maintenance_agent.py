"""
ATLAS MAINTENANCE AGENT - Real-World System Setup & Integration
================================================================
Autonomous agent that handles:
- API key collection and setup
- Account creation for third-party services
- Real-world integration configuration
- Browser automation for manual setup tasks
- System configuration management
- Operational requirements gathering
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from .browser_automation_system import get_browser_automation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceRequirement:
    """Represents a service that needs to be set up"""

    name: str
    purpose: str
    api_keys_needed: List[str]
    setup_url: str
    setup_steps: List[str]
    priority: str  # critical, high, medium, low
    status: str = "pending"  # pending, in_progress, completed, failed
    notes: str = ""
    credentials: Dict[str, str] = None

    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}


class AtlasMaintenanceAgent:
    """
    ATLAS - Autonomous Technical & Logistics Agent for System Setup

    Capabilities:
    - Browser automation and navigation
    - Account creation and API key retrieval
    - System configuration management
    - Real-world integration setup
    - Automated requirement fulfillment
    """

    def __init__(self):
        self.name = "ATLAS"
        self.role = "Maintenance & Setup Specialist"
        self.capabilities = [
            "Browser Automation",
            "API Key Management",
            "Account Creation",
            "System Configuration",
            "Integration Testing",
            "Requirement Analysis",
        ]

        self.setup_progress = {
            "total_requirements": 0,
            "completed": 0,
            "in_progress": 0,
            "failed": 0,
            "completion_percentage": 0,
        }

        # Define all real-world requirements
        self.requirements = self._define_system_requirements()
        self.config_file = "data/system_config.json"
        self.setup_log_file = "data/atlas_setup_log.json"

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        logger.info(f"🔧 {self.name} Maintenance Agent initialized")
        logger.info(
            f"📋 Identified {len(self.requirements)} critical system requirements"
        )

    def _define_system_requirements(self) -> List[ServiceRequirement]:
        """Define all services and APIs needed for real-world operation"""

        requirements = [
            ServiceRequirement(
                name="Stripe Payment Processing",
                purpose="Process real payments and handle customer transactions",
                api_keys_needed=[
                    "STRIPE_SECRET_KEY",
                    "STRIPE_PUBLISHABLE_KEY",
                    "STRIPE_WEBHOOK_SECRET",
                ],
                setup_url="https://dashboard.stripe.com/register",
                setup_steps=[
                    "Create Stripe account",
                    "Verify business information",
                    "Navigate to API Keys section",
                    "Copy Secret Key and Publishable Key",
                    "Set up webhook endpoints",
                    "Configure payment methods",
                ],
                priority="critical",
            ),
            ServiceRequirement(
                name="Ollama Local Model Server",
                purpose="Run AI agents with locally hosted open-weight models",
                api_keys_needed=[],
                setup_url="https://ollama.ai/download",
                setup_steps=[
                    "Install Ollama on the host machine",
                    "Start the Ollama service",
                    "Run 'ollama pull llama3.1:8b' (or preferred model)",
                    "Set LLM_PROVIDER=ollama and optional OLLAMA_BASE_URL",
                    "Confirm the server responds on http://localhost:11434",
                ],
                priority="critical",
            ),
            ServiceRequirement(
                name="SendGrid Email Service",
                purpose="Send marketing emails and transactional messages",
                api_keys_needed=["SENDGRID_API_KEY"],
                setup_url="https://signup.sendgrid.com/",
                setup_steps=[
                    "Create SendGrid account",
                    "Verify email address",
                    "Navigate to Settings > API Keys",
                    "Create new API key with Mail Send permissions",
                    "Set up sender authentication",
                ],
                priority="high",
            ),
            ServiceRequirement(
                name="Twitter API (X)",
                purpose="Automated social media marketing",
                api_keys_needed=[
                    "TWITTER_API_KEY",
                    "TWITTER_API_SECRET",
                    "TWITTER_ACCESS_TOKEN",
                    "TWITTER_ACCESS_SECRET",
                ],
                setup_url="https://developer.twitter.com/en/portal/dashboard",
                setup_steps=[
                    "Apply for Twitter Developer Account",
                    "Create new App/Project",
                    "Generate API keys and tokens",
                    "Set up OAuth permissions",
                    "Test API access",
                ],
                priority="high",
            ),
            ServiceRequirement(
                name="Google Analytics",
                purpose="Track website traffic and user behavior",
                api_keys_needed=["GOOGLE_ANALYTICS_ID", "GOOGLE_API_KEY"],
                setup_url="https://analytics.google.com/",
                setup_steps=[
                    "Create Google Analytics account",
                    "Set up property and data stream",
                    "Get tracking ID",
                    "Enable API access",
                    "Create service account credentials",
                ],
                priority="medium",
            ),
            ServiceRequirement(
                name="Webhooks.site Testing",
                purpose="Test webhook integrations during development",
                api_keys_needed=["WEBHOOK_TEST_URL"],
                setup_url="https://webhook.site/",
                setup_steps=[
                    "Generate unique webhook URL",
                    "Test webhook reception",
                    "Configure webhook endpoints in system",
                ],
                priority="low",
            ),
            ServiceRequirement(
                name="Domain Registration",
                purpose="Professional domain for business operations",
                api_keys_needed=["DOMAIN_NAME", "DNS_PROVIDER"],
                setup_url="https://www.namecheap.com/",
                setup_steps=[
                    "Search and register domain name",
                    "Set up DNS configuration",
                    "Configure SSL certificate",
                    "Point domain to server",
                ],
                priority="medium",
            ),
            ServiceRequirement(
                name="AWS/CloudFlare CDN",
                purpose="Host files and improve site performance",
                api_keys_needed=["AWS_ACCESS_KEY", "AWS_SECRET_KEY"],
                setup_url="https://aws.amazon.com/",
                setup_steps=[
                    "Create AWS account",
                    "Set up S3 bucket for file storage",
                    "Configure CloudFront distribution",
                    "Generate access keys",
                    "Set up IAM permissions",
                ],
                priority="medium",
            ),
        ]

        return requirements

    def get_setup_dashboard_html(self) -> str:
        """Generate HTML dashboard for setup progress monitoring"""

        # Update progress metrics
        self.setup_progress["total_requirements"] = len(self.requirements)
        self.setup_progress["completed"] = sum(
            1 for r in self.requirements if r.status == "completed"
        )
        self.setup_progress["in_progress"] = sum(
            1 for r in self.requirements if r.status == "in_progress"
        )
        self.setup_progress["failed"] = sum(
            1 for r in self.requirements if r.status == "failed"
        )

        if self.setup_progress["total_requirements"] > 0:
            self.setup_progress["completion_percentage"] = round(
                (
                    self.setup_progress["completed"]
                    / self.setup_progress["total_requirements"]
                )
                * 100,
                1,
            )

        requirements_html = ""
        for req in self.requirements:
            status_color = {
                "pending": "#fbbf24",
                "in_progress": "#3b82f6",
                "completed": "#10b981",
                "failed": "#ef4444",
            }.get(req.status, "#6b7280")

            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌",
            }.get(req.status, "⚪")

            priority_color = {
                "critical": "#dc2626",
                "high": "#ea580c",
                "medium": "#d97706",
                "low": "#65a30d",
            }.get(req.priority, "#6b7280")

            requirements_html += f'''
            <div class="requirement-card" style="border-left: 4px solid {status_color};">
                <div class="req-header">
                    <div class="req-title">
                        <span class="status-icon">{status_icon}</span>
                        <strong>{req.name}</strong>
                        <span class="priority-badge" style="background-color: {priority_color};">{req.priority.upper()}</span>
                    </div>
                    <button class="action-btn" onclick="setupService('{req.name}')">
                        {"🔄 RESUME" if req.status == "in_progress" else "🚀 START SETUP"}
                    </button>
                </div>
                <div class="req-purpose">{req.purpose}</div>
                <div class="req-details">
                    <div><strong>API Keys Needed:</strong> {", ".join(req.api_keys_needed)}</div>
                    <div><strong>Setup URL:</strong> <a href="{req.setup_url}" target="_blank">{req.setup_url}</a></div>
                    {"<div><strong>Notes:</strong> " + req.notes + "</div>" if req.notes else ""}
                </div>
                <div class="req-steps">
                    <strong>Setup Steps:</strong>
                    <ol>
                        {"".join(f"<li>{step}</li>" for step in req.setup_steps)}
                    </ol>
                </div>
            </div>
            '''

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 ATLAS Maintenance - System Setup</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            color: #e0e7ff; min-height: 100vh;
        }}
        
        .header {{ 
            background: linear-gradient(90deg, #3730a3 0%, #1e1b4b 100%);
            padding: 2rem; text-align: center; border-bottom: 3px solid #6366f1;
        }}
        .header h1 {{ color: #6366f1; font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header .tagline {{ color: #a5b4fc; font-size: 1.1rem; }}
        
        .progress-section {{ 
            padding: 2rem; background: rgba(99,102,241,0.1); 
            border-bottom: 1px solid #4c1d95;
        }}
        .progress-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; max-width: 1000px; margin: 0 auto;
        }}
        .progress-card {{ 
            background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 10px;
            text-align: center; border: 1px solid #6366f1;
        }}
        .progress-number {{ font-size: 2.5rem; font-weight: bold; color: #6366f1; }}
        .progress-label {{ color: #a5b4fc; margin-top: 0.5rem; }}
        
        .main-content {{ padding: 2rem; max-width: 1200px; margin: 0 auto; }}
        
        .control-panel {{ 
            background: rgba(99,102,241,0.1); padding: 1.5rem; border-radius: 10px; 
            margin-bottom: 2rem; border: 1px solid #6366f1;
        }}
        .control-panel h2 {{ color: #6366f1; margin-bottom: 1rem; }}
        .control-buttons {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
        .control-btn {{ 
            padding: 1rem 1.5rem; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: all 0.3s;
            background: linear-gradient(45deg, #6366f1, #8b5cf6);
            color: white; font-size: 1rem;
        }}
        .control-btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.3); }}
        
        .requirements-section h2 {{ color: #6366f1; margin-bottom: 1.5rem; }}
        
        .requirement-card {{ 
            background: rgba(255,255,255,0.05); margin: 1rem 0; 
            border-radius: 10px; padding: 1.5rem; border: 1px solid #4c1d95;
        }}
        .req-header {{ 
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 1rem;
        }}
        .req-title {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
        .status-icon {{ font-size: 1.2rem; }}
        .priority-badge {{ 
            font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;
            color: white; font-weight: bold;
        }}
        .action-btn {{ 
            padding: 0.5rem 1rem; border: none; border-radius: 6px;
            background: linear-gradient(45deg, #10b981, #059669);
            color: white; font-weight: 600; cursor: pointer;
        }}
        .action-btn:hover {{ opacity: 0.9; }}
        
        .req-purpose {{ color: #a5b4fc; margin-bottom: 1rem; font-style: italic; }}
        .req-details {{ margin-bottom: 1rem; }}
        .req-details > div {{ margin: 0.3rem 0; }}
        .req-details a {{ color: #6366f1; text-decoration: none; }}
        .req-details a:hover {{ text-decoration: underline; }}
        
        .req-steps ol {{ margin-left: 1.5rem; }}
        .req-steps li {{ margin: 0.3rem 0; }}
        
        .status-pending {{ border-left-color: #fbbf24 !important; }}
        .status-in-progress {{ border-left-color: #3b82f6 !important; }}
        .status-completed {{ border-left-color: #10b981 !important; }}
        .status-failed {{ border-left-color: #ef4444 !important; }}
        
        @media (max-width: 768px) {{
            .control-buttons {{ flex-direction: column; }}
            .req-header {{ flex-direction: column; align-items: stretch; gap: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 ATLAS MAINTENANCE AGENT</h1>
        <div class="tagline">Autonomous System Setup & Real-World Integration Specialist</div>
    </div>
    
    <div class="progress-section">
        <div class="progress-grid">
            <div class="progress-card">
                <div class="progress-number">{self.setup_progress["total_requirements"]}</div>
                <div class="progress-label">Total Requirements</div>
            </div>
            <div class="progress-card">
                <div class="progress-number">{self.setup_progress["completed"]}</div>
                <div class="progress-label">Completed</div>
            </div>
            <div class="progress-card">
                <div class="progress-number">{self.setup_progress["in_progress"]}</div>
                <div class="progress-label">In Progress</div>
            </div>
            <div class="progress-card">
                <div class="progress-number">{self.setup_progress["completion_percentage"]}%</div>
                <div class="progress-label">Complete</div>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="control-panel">
            <h2>🎛️ Maintenance Control Panel</h2>
            <div class="control-buttons">
                <button class="control-btn" onclick="startAutomatedSetup()">🤖 START AUTOMATED SETUP</button>
                <button class="control-btn" onclick="testBrowserAutomation()">🌐 TEST BROWSER AUTOMATION</button>
                <button class="control-btn" onclick="generateConfigFile()">⚙️ GENERATE CONFIG FILE</button>
                <button class="control-btn" onclick="validateCredentials()">✅ VALIDATE CREDENTIALS</button>
                <button class="control-btn" onclick="exportSetupReport()">📄 EXPORT SETUP REPORT</button>
                <button class="control-btn" onclick="viewSystemLogs()">📋 VIEW SYSTEM LOGS</button>
            </div>
        </div>
        
        <div class="requirements-section">
            <h2>📋 System Requirements & Setup Status</h2>
            {requirements_html}
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(() => {{
            location.reload();
        }}, 30000);

        function startAutomatedSetup() {{
            if (confirm('🤖 ATLAS will now begin automated setup process. This will open browser windows and navigate websites automatically. Continue?')) {{
                fetch('/api/atlas/start_automated_setup', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}}
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('✅ Automated setup initiated! Check progress in real-time.');
                    location.reload();
                }})
                .catch(error => alert('❌ Setup failed: ' + error.message));
            }}
        }}

        function setupService(serviceName) {{
            if (confirm(`🔧 Begin setup for ${{serviceName}}? ATLAS will open the browser and guide you through the process.`)) {{
                fetch('/api/atlas/setup_service', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{service: serviceName}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(`🚀 Setup started for ${{serviceName}}. Follow ATLAS guidance in the browser.`);
                    location.reload();
                }})
                .catch(error => alert('❌ Setup failed: ' + error.message));
            }}
        }}

        function testBrowserAutomation() {{
            fetch('/api/atlas/test_browser', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
            }})
            .then(response => response.json())
            .then(data => {{
                alert('🌐 Browser automation test completed! Check system logs for results.');
            }})
            .catch(error => alert('❌ Browser test failed: ' + error.message));
        }}

        function generateConfigFile() {{
            fetch('/api/atlas/generate_config', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
            }})
            .then(response => response.json())
            .then(data => {{
                alert('⚙️ Configuration file generated successfully!');
            }})
            .catch(error => alert('❌ Config generation failed: ' + error.message));
        }}

        function validateCredentials() {{
            fetch('/api/atlas/validate_credentials', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
            }})
            .then(response => response.json())
            .then(data => {{
                alert(`✅ Credential validation completed. Results: ${{data.status}}`);
            }})
            .catch(error => alert('❌ Validation failed: ' + error.message));
        }}

        function exportSetupReport() {{
            window.open('/api/atlas/setup_report', '_blank');
        }}

        function viewSystemLogs() {{
            window.open('/api/atlas/logs', '_blank');
        }}
    </script>
</body>
</html>
        """

        return html_content

    def start_automated_setup(self) -> Dict[str, Any]:
        """Begin automated setup process for all critical requirements"""

        logger.info("🤖 ATLAS: Starting automated setup process...")

        # Update status for critical requirements
        critical_requirements = [
            r for r in self.requirements if r.priority == "critical"
        ]

        setup_plan = {
            "timestamp": datetime.now().isoformat(),
            "action": "automated_setup_started",
            "critical_services": len(critical_requirements),
            "total_services": len(self.requirements),
            "estimated_time": "15-30 minutes",
            "next_steps": [],
        }

        for req in critical_requirements:
            req.status = "in_progress"
            req.notes = (
                f"Automated setup started at {datetime.now().strftime('%H:%M:%S')}"
            )

            setup_plan["next_steps"].append(
                {
                    "service": req.name,
                    "action": "navigate_and_setup",
                    "url": req.setup_url,
                    "priority": req.priority,
                }
            )

        # Log the setup initiation
        self._log_setup_action("automated_setup_started", setup_plan)

        return {
            "status": "success",
            "message": "Automated setup process initiated",
            "plan": setup_plan,
        }

    async def setup_service_with_browser(self, service_name: str) -> Dict[str, Any]:
        """Set up a specific service using browser automation"""

        service_req = next(
            (r for r in self.requirements if r.name == service_name), None
        )
        if not service_req:
            return {"status": "error", "message": f"Service '{service_name}' not found"}

        logger.info(f"🌐 ATLAS: Starting browser-automated setup for {service_name}")

        service_req.status = "in_progress"
        service_req.notes = (
            f"Browser automation started at {datetime.now().strftime('%H:%M:%S')}"
        )

        # Get browser automation system
        browser_automation = get_browser_automation()

        # Run guided setup
        automation_result = await browser_automation.run_guided_setup(service_name)

        # Get automation guidance
        guidance = browser_automation.get_automation_guidance(service_name)

        # Log the setup action
        setup_action = {
            "timestamp": datetime.now().isoformat(),
            "action": "browser_automation_initiated",
            "service": service_name,
            "url": service_req.setup_url,
            "automation_plan": automation_result.get("automation_plan", {}),
            "browser_automation": True,
        }

        self._log_setup_action("service_setup", setup_action)

        return {
            "status": "success",
            "message": f"Browser automation initiated for {service_name}",
            "service": service_req.name,
            "url": service_req.setup_url,
            "automation_plan": automation_result.get("automation_plan", {}),
            "guidance": guidance,
            "next_steps": [
                "ATLAS will open a browser window",
                "Follow the automated setup process",
                "Provide manual input when prompted",
                "API keys will be collected automatically",
            ],
        }

    async def test_browser_automation(self) -> Dict[str, Any]:
        """Test browser automation capabilities"""

        logger.info("🧪 ATLAS: Testing browser automation capabilities...")

        # Get browser automation system and run tests
        browser_automation = get_browser_automation()
        test_results = await browser_automation.test_browser_capabilities()

        self._log_setup_action("browser_automation_test", test_results)

        return {
            "status": "success",
            "message": "Browser automation test completed",
            "results": test_results,
            "capabilities_verified": len(
                [t for t in test_results["tests"] if t["status"] == "operational"]
            ),
            "automation_ready": test_results["automation_ready"],
        }

    def generate_config_file(self) -> Dict[str, Any]:
        """Generate system configuration file template"""

        config_template = {
            "system_info": {
                "setup_date": datetime.now().isoformat(),
                "atlas_version": "1.0.0",
                "status": "configuration_template",
            },
            "api_credentials": {},
            "service_configurations": {},
            "environment_variables": {},
        }

        # Add placeholders for all required API keys
        for req in self.requirements:
            for api_key in req.api_keys_needed:
                config_template["api_credentials"][api_key] = {
                    "value": f"INSERT_{api_key}_HERE",
                    "service": req.name,
                    "required": req.priority in ["critical", "high"],
                    "setup_url": req.setup_url,
                }

                # Add as environment variable template
                config_template["environment_variables"][api_key] = (
                    f"INSERT_{api_key}_HERE"
                )

        # Save configuration template
        with open(self.config_file, "w") as f:
            json.dump(config_template, f, indent=2)

        logger.info(f"⚙️ ATLAS: Configuration template saved to {self.config_file}")

        return {
            "status": "success",
            "message": "Configuration template generated",
            "file_path": self.config_file,
            "api_keys_count": len(config_template["api_credentials"]),
        }

    def validate_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials"""

        logger.info("✅ ATLAS: Validating system credentials...")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_credentials": 0,
            "valid": 0,
            "invalid": 0,
            "missing": 0,
            "details": [],
        }

        # Check each requirement's credentials
        for req in self.requirements:
            for api_key in req.api_keys_needed:
                validation_results["total_credentials"] += 1

                # Check if credential exists in environment or config
                env_value = os.environ.get(api_key)
                config_value = None

                if os.path.exists(self.config_file):
                    with open(self.config_file, "r") as f:
                        config = json.load(f)
                        config_value = (
                            config.get("api_credentials", {})
                            .get(api_key, {})
                            .get("value")
                        )

                if env_value and not env_value.startswith("INSERT_"):
                    validation_results["valid"] += 1
                    status = "valid"
                elif config_value and not config_value.startswith("INSERT_"):
                    validation_results["valid"] += 1
                    status = "valid"
                else:
                    validation_results["missing"] += 1
                    status = "missing"

                validation_results["details"].append(
                    {
                        "credential": api_key,
                        "service": req.name,
                        "status": status,
                        "source": "environment"
                        if env_value
                        else "config"
                        if config_value
                        else "none",
                    }
                )

        self._log_setup_action("credential_validation", validation_results)

        return {
            "status": "success",
            "message": "Credential validation completed",
            "results": validation_results,
        }

    def _log_setup_action(self, action_type: str, details: Dict[str, Any]):
        """Log setup actions to file"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action_type": action_type,
            "details": details,
        }

        logs = []
        if os.path.exists(self.setup_log_file):
            with open(self.setup_log_file, "r") as f:
                logs = json.load(f)

        logs.append(log_entry)

        # Keep only last 500 entries
        if len(logs) > 500:
            logs = logs[-500:]

        with open(self.setup_log_file, "w") as f:
            json.dump(logs, f, indent=2)

    def get_setup_report(self) -> Dict[str, Any]:
        """Generate comprehensive setup report"""

        report = {
            "generation_timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "system_status": "setup_in_progress",
            "progress_summary": self.setup_progress.copy(),
            "requirements_by_priority": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
            },
            "next_actions": [],
            "estimated_completion": "TBD based on setup progress",
        }

        # Organize requirements by priority and status
        for req in self.requirements:
            req_summary = {
                "name": req.name,
                "status": req.status,
                "purpose": req.purpose,
                "api_keys_count": len(req.api_keys_needed),
                "setup_url": req.setup_url,
                "notes": req.notes,
            }
            report["requirements_by_priority"][req.priority].append(req_summary)

            # Add to next actions if not completed
            if req.status != "completed":
                report["next_actions"].append(
                    {
                        "service": req.name,
                        "priority": req.priority,
                        "action_needed": "complete_setup"
                        if req.status == "in_progress"
                        else "start_setup",
                        "url": req.setup_url,
                    }
                )

        return report


# Global instance
atlas_agent = AtlasMaintenanceAgent()


def get_atlas_agent():
    """Get the global ATLAS maintenance agent instance"""
    return atlas_agent
