import { EventBus } from '@earnetics/core';
import { v4 as uuidv4 } from 'uuid';

export class Simulator {
    private interval: NodeJS.Timeout | null = null;

    constructor(private eventBus: EventBus) { }

    start() {
        if (this.interval) return;

        console.log('Starting Simulator...');

        // Initial Objective
        this.eventBus.publish('OBJECTIVE_CREATED', {
            id: uuidv4(),
            title: 'Maximize Q4 Revenue',
            priority: 'high',
            status: 'active',
            createdAt: Date.now(),
            tags: ['revenue', 'q4']
        });

        this.interval = setInterval(() => {
            const eventTypes = [
                'TASK_STARTED',
                'TASK_COMPLETED',
                'AGENT_HEARTBEAT',
                'ARTIFACT_CREATED',
                'KPI_UPDATED'
            ];

            const type = eventTypes[Math.floor(Math.random() * eventTypes.length)];
            const payload = this.generatePayload(type);

            this.eventBus.publish(type, payload);
        }, 3000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    private generatePayload(type: string): any {
        switch (type) {
            case 'TASK_STARTED':
                return { taskId: uuidv4(), agentId: 'agent-001', timestamp: Date.now() };
            case 'TASK_COMPLETED':
                return { taskId: uuidv4(), result: 'success', timestamp: Date.now() };
            case 'AGENT_HEARTBEAT':
                return { agentId: 'agent-001', status: 'working', load: Math.random() };
            case 'ARTIFACT_CREATED':
                return { artifactId: uuidv4(), type: 'report', uri: 'file:///reports/q4.pdf' };
            case 'KPI_UPDATED':
                return { kpiId: 'revenue', value: Math.floor(Math.random() * 10000) };
            default:
                return {};
        }
    }
}
