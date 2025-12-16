import { AppEvent, Task, Agent } from './types';

export class ReadModelStore {
    tasks: Map<string, Task> = new Map();
    agents: Map<string, Agent> = new Map();
    departments: Set<string> = new Set();

    handleEvent(event: AppEvent) {
        switch (event.type) {
            case 'SYSTEM_READY':
                if (event.payload.agents) {
                    event.payload.agents.forEach((agent: any) => {
                        this.agents.set(agent.id, agent);
                    });
                }
                if (event.payload.departments) {
                    event.payload.departments.forEach((dept: string) => {
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
                    this.tasks.set(event.payload.id, { ...this.tasks.get(event.payload.id)!, ...event.payload });
                }
                break;
        }
    }

    getAgents(): Agent[] {
        return Array.from(this.agents.values());
    }

    getDepartments(): string[] {
        return Array.from(this.departments);
    }

    reset() {
        this.tasks.clear();
        this.agents.clear();
        this.departments.clear();
    }
}

export function rebuild_read_models(events: AppEvent[]): ReadModelStore {
    const store = new ReadModelStore();
    store.reset();

    for (const event of events) {
        store.handleEvent(event);
    }

    return store;
}
