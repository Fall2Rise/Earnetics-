export class ReadModelStore {
    tasks = new Map();
    agents = new Map();
    departments = new Set();
    handleEvent(event) {
        switch (event.type) {
            case 'SYSTEM_READY':
                if (event.payload.agents) {
                    event.payload.agents.forEach((agent) => {
                        this.agents.set(agent.id, agent);
                    });
                }
                if (event.payload.departments) {
                    event.payload.departments.forEach((dept) => {
                        this.departments.add(dept);
                    });
                }
                break;
            case 'TASK_CREATED':
                const task = event.payload;
                this.tasks.set(task.id, task);
                break;
            case 'TASK_UPDATED':
                if (this.tasks.has(event.payload.id)) {
                    this.tasks.set(event.payload.id, { ...this.tasks.get(event.payload.id), ...event.payload });
                }
                break;
        }
    }
    getAgents() {
        return Array.from(this.agents.values());
    }
    getDepartments() {
        return Array.from(this.departments);
    }
    reset() {
        this.tasks.clear();
        this.agents.clear();
        this.departments.clear();
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
