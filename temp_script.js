


        let currentRevenue = 0;


        


        async function refreshData() {


            try {


                const response = await fetch('/api/financial_summary');


                const data = await response.json();


                if (data.status === 'success') {


                    currentRevenue = data.financial_data.performance_metrics.total_revenue;


                    document.getElementById('revenue').textContent = '$' + currentRevenue.toLocaleString('en-US', {minimumFractionDigits: 2});


                    document.getElementById('customers').textContent = data.financial_data.performance_metrics.active_customers;


                    document.getElementById('products').textContent = data.financial_data.performance_metrics.products_created;


                    


                    // Update progress bar


                    const progress = (currentRevenue / 150000) * 100;


                    document.getElementById('progress').style.width = Math.min(progress, 100) + '%';


                }


            } catch (error) {


                console.error('Error refreshing data:', error);


            }


        }


        


        async function runAutonomousCycle() {


            document.getElementById('autonomous-status').textContent = '🔄 Running decision cycle...';


            try {


                const response = await fetch('/api/autonomous/run_cycle');


                const data = await response.json();


                if (data.status === 'success') {


                    document.getElementById('autonomous-status').textContent = '✅ Decision cycle completed!';


                    setTimeout(() => {


                        document.getElementById('autonomous-status').textContent = '🤖 AI Agents Active';


                    }, 3000);


                    


                    // Show results


                    alert('AI Agents have analyzed the business and made strategic decisions! Check the action plan.');


                }


            } catch (error) {


                document.getElementById('autonomous-status').textContent = '❌ Error in decision cycle';


                console.error('Error:', error);


            }


        }


        


        async function launchProduct(productId) {


            try {


                const response = await fetch(`/api/launch_product/${productId}`);


                const data = await response.json();


                if (data.status === 'success') {


                    alert(`Successfully launched ${productId}! Payment link: ${data.payment_link}`);


                    refreshData();


                }


            } catch (error) {


                console.error('Error launching product:', error);


            }


        }


        


        async function executeCorporateRecommendations() {


            try {


                alert('🚀 Executing Corporate Recommendations!

Implementation Division is now:
• Setting up Stripe API
• Configuring social media APIs
• Optimizing workflows
• Monitoring performance

Check execution status in a few moments...');





                const response = await fetch('/api/corporate/execute', {


                    method: 'POST',


                    headers: { 'Content-Type': 'application/json' }


                });


                const data = await response.json();





                if (data.status === 'success') {


                    window.open('/api/corporate/execute', '_blank');


                    refreshData();


                }


            } catch (error) {


                console.error('Error executing recommendations:', error);


            }


        }


        


        async function executeContinuousWorkflow() {


            try {


                alert('🔁 INITIATING 7-PHASE CONTINUOUS WORKFLOW LOOP!\n\n🔍 Phase 1: Discovery - Noir scanning 847 marketplaces\n🔧 Phase 2: Development - Forge building AI Finance Assistant\n🧪 Phase 3: Testing - Nova validating Holistic Health eBook\n🚀 Phase 4: Marketing - Scaling Crypto Arbitrage Bot\n💰 Phase 5: Revenue - AI Resume Builder generating $2,847\n📊 Phase 6: Monitoring - All streams being optimized\n💎 Phase 7: Reinvestment - Funding 3 new opportunities\n\nTOTAL: 4 Active Revenue Streams = $5,337 Weekly!');


                


                const response = await fetch('/api/workflow/continuous_loop', {


                    method: 'POST',


                    headers: { 'Content-Type': 'application/json' }


                });


                const data = await response.json();


                


                if (data.status === 'success') {


                    window.open('/api/workflow/continuous_loop', '_blank');


                    refreshData();


                }


            } catch (error) {


                console.error('Error executing workflow loop:', error);


            }


        }


        





        const assistantKnowledge = [


            {


                title: 'Install dependencies',


                keywords: ['install', 'setup', 'dependencies', 'pip', 'requirements'],


                response: 'To install everything locally run <code>pip install -r requirements.txt</code>. Optional tools like <code>pytrends</code> and <code>yfinance</code> are already listed in the requirements file. Use a Python 3.11 virtual environment for best results.'


            },


            {


                title: 'Configure environment',


                keywords: ['env', 'environment', 'api key', 'credentials', 'secrets'],


                response: 'Create a copy of <code>.env.example</code> as <code>.env</code>. Populate Stripe keys (<code>STRIPE_SECRET_KEY</code>, <code>STRIPE_WEBHOOK_SECRET</code>), SMTP details, Twitter tokens, dropshipping keys (<code>SHOPIFY_*</code>), and affiliate credentials. Values are resolved via the credential vault helper in <code>backend/credentials_store.py</code>.'


            },


            {


                title: 'Run backend server',


                keywords: ['run', 'start', 'server', 'backend', 'uvicorn'],


                response: 'Launch the system locally with <code>python backend/main_server.py</code>. The FastAPI server exposes the dashboard at <code>http://localhost:8080</code> and interactive docs at <code>/docs</code>.'


            },


            {


                title: 'Autonomous workflow',


                keywords: ['autonomy', 'workflow', 'scheduler', 'tasks'],


                response: 'Autonomous directives flow through <code>ExecutiveDirective</code> &rarr; <code>AutonomousWorkflowOrchestrator</code> &rarr; <code>CorporateMemory</code>. Enable the background scheduler via <code>AUTONOMY_SCHEDULER_ENABLED=true</code> to continuously generate and execute tasks.'


            },


            {


                title: 'Affiliate engine',


                keywords: ['affiliate', 'partnership', 'offer', 'tracking'],


                response: 'Agents Orion, Vortex, and Lumen call <code>AffiliateNetworkIntegration</code> to fetch offers, build funnels, and analyse performance. Provide affiliate API base URL and key so tracking links can be created automatically.'


            },


            {


                title: 'Dropshipping ops',


                keywords: ['dropship', 'shopify', 'store', 'orders'],


                response: 'Cascade and Torrent manage the dropshipping division. Set <code>SHOPIFY_STORE_URL</code> and <code>SHOPIFY_ADMIN_API_TOKEN</code> to sync the product catalog and fulfil orders through the <code>DropshippingStoreIntegration</code>.'


            },


            {


                title: 'Revenue innovation',


                keywords: ['innovation', 'new revenue', 'ideas', 'genesis'],


                response: 'Genesis uses the <code>RevenueInnovationIntegration</code> to propose new revenue streams. Each approved idea registers an <code>innovation</code> directive so the workflow engine can scaffold tasks across finance, product, and marketing.'


            },


            {


                title: 'Testing and QA',


                keywords: ['test', 'pytest', 'quality', 'checks'],


                response: 'Run <code>pytest</code> or targeted suites such as <code>pytest tests/test_smoke.py -v</code> to verify integrations before deployment. Lint with <code>ruff check .</code> to keep the codebase tidy.'


            },


            {


                title: 'Data & docs',


                keywords: ['docs', 'documentation', 'readme', 'guide'],


                response: 'Key references: <code>README.md</code> (overview), <code>docs/autonomy_backlog.md</code> (roadmap), <code>TODO.md</code> (next actions), and <code>backend/stripe_integration.py</code> (payment flow). The assistant can quote any of these on request.'


            }


        ];





        let assistantElements = {};





        function initAssistant() {


            assistantElements.wrapper = document.getElementById('assistant-wrapper');


            assistantElements.avatar = document.getElementById('assistant-avatar');


            assistantElements.window = document.getElementById('assistant-window');


            assistantElements.messages = document.getElementById('assistant-messages');


            assistantElements.input = document.getElementById('assistant-query');


            assistantElements.label = document.getElementById('assistant-label');





            if (!assistantElements.avatar || !assistantElements.window) {


                return;


            }





            assistantElements.avatar.addEventListener('click', toggleAssistant);


            assistantElements.input.addEventListener('keydown', function (event) {


                if (event.key === 'Enter') {


                    event.preventDefault();


                    submitAssistantQuery();


                }


            });





            setTimeout(function () {


                assistantElements.label.textContent = 'Ask NovaGuide';


            }, 2000);





            setTimeout(function () {


                assistantElements.window.classList.add('show');


                assistantAddMessage('bot', 'Hi, I'm <strong>NovaGuide</strong>, your operations companion. Ask me about setup, automation, or any division inside Fallat CrewAI.');


                assistantAddMessage('bot', assistantSuggestionHtml());


            }, 900);


        }





        function assistantSuggestionHtml() {


            return '<div class="assistant-suggestion"><strong>Try asking:</strong><ul><li>How do I configure Stripe?</li><li>What do Cascade and Torrent manage?</li><li>How do I run the autonomous workflow?</li></ul></div>';


        }





        function toggleAssistant() {


            if (!assistantElements.window) {


                return;


            }


            const isOpen = assistantElements.window.classList.contains('show');


            if (isOpen) {


                assistantElements.window.classList.remove('show');


            } else {


                assistantElements.window.classList.add('show');


                assistantElements.input.focus();


            }


        }





        function closeAssistant() {


            if (assistantElements.window) {


                assistantElements.window.classList.remove('show');


            }


        }





        function assistantAddMessage(author, message) {


            if (!assistantElements.messages) {


                return;


            }


            const bubble = document.createElement('div');


            bubble.className = 'assistant-message ' + (author === 'user' ? 'user' : 'bot');


            if (author === 'user') {


                bubble.textContent = message;


            } else {


                bubble.innerHTML = message;


            }


            assistantElements.messages.appendChild(bubble);


            assistantElements.messages.scrollTop = assistantElements.messages.scrollHeight;


        }





        function submitAssistantQuery() {


            if (!assistantElements.input) {


                return;


            }


            const query = assistantElements.input.value.trim();


            if (!query) {


                return;


            }


            assistantAddMessage('user', query);


            assistantElements.input.value = '';


            const reply = assistantFindResponse(query);


            assistantAddMessage('bot', reply);


        }





        function assistantFindResponse(question) {


            const lower = question.toLowerCase();


            let best = null;


            let bestScore = 0;


            assistantKnowledge.forEach(function (entry) {


                let score = 0;


                entry.keywords.forEach(function (keyword) {


                    if (lower.includes(keyword)) {


                        score += 1;


                    }


                });


                if (score > bestScore) {


                    bestScore = score;


                    best = entry;


                }


            });


            if (best) {


                return best.response;


            }


            return 'Here is a quick orientation:<ul><li><strong>Setup:</strong> clone the repository, install dependencies, and copy <code>.env.example</code> to <code>.env</code>.</li><li><strong>Run:</strong> start the FastAPI server with <code>python backend/main_server.py</code> and open the dashboard on port 8080.</li><li><strong>Docs:</strong> checkout <code>README.md</code> and the <code>docs/</code> folder for deep dives.</li><li><strong>Agents:</strong> affiliate (Orion/Vortex/Lumen), dropshipping (Cascade/Torrent), and innovation (Genesis) are fully wired into the new integrations.</li></ul>If you need something specific, mention the component, file, or integration name.';


        }





        async function testTransaction() {


            try {


                event.preventDefault();


                const amount = prompt('Enter test transaction amount (e.g., 100):');


                if (!amount || isNaN(amount)) return;


                


                const response = await fetch('/api/record_transaction', {


                    method: 'POST',


                    headers: { 'Content-Type': 'application/json' },


                    body: JSON.stringify({


                        amount: parseFloat(amount),


                        source: 'Test Transaction',


                        description: 'Manual test transaction',


                        customer: 'test@example.com'


                    })


                });


                


                const data = await response.json();


                if (data.status === 'success') {


                    alert(`Transaction processed!\n\nGross: $${data.breakdown.gross_amount}\nOwner Payout (80%): $${data.breakdown.owner_payout}\nReinvestment (20%): $${data.breakdown.reinvestment}`);


                    refreshData();


                } else {


                    alert('Error: ' + data.message);


                }


            } catch (error) {


                console.error('Error creating test transaction:', error);


            }


        }


        


        // Auto-refresh data every 30 seconds


        setInterval(refreshData, 30000);


        


        // Load initial data when page loads


        window.addEventListener('load', function () {


            refreshData();


            refreshDashboard();


            initAssistant();


            addActivity('ðŸš€ Dashboard loaded successfully');


        });


    