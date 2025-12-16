export class ReadModelStore {
    tasks = new Map();
    agents = new Map();
    handleEvent(event) {
        switch (event.type) {
            case 'TASK_STARTED':
                // Update task state
                break;
            case 'AGENT_HEARTBEAT':
                // Update agent state
                break;
        }
    }
    reset() {
        this.tasks.clear();
        this.agents.clear();
    }
}
export function rebuild_read_models(events) {
    const store = new ReadModelStore();
    store.reset();
    for (const event of events) {
        store.handleEvent(event);
    }
    return store;
}
