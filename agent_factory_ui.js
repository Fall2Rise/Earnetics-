// Add this to the command center dashboard to enable agent factory

async function createNewAgent() {
    const name = prompt("Agent Name:");
    const role = prompt("Agent Role:");
    const purpose = prompt("What should this agent do?");

    if (!name || !role || !purpose) return;

    const response = await fetch('/atom/generate_agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_name: name,
            agent_role: role,
            agent_purpose: purpose
        })
    });

    const result = await response.json();
    alert(`Agent Created: ${result.agent_file || 'Check logs'}`);
}

async function createRevenueStream() {
    const name = prompt("Revenue Stream Name:");
    const note = prompt("Description:");

    if (!name) return;

    const response = await fetch('/api/factory/streams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, note: note || '' })
    });

    const result = await response.json();
    alert(`Stream Created: ${result.name} (ID: ${result.id})`);
}
