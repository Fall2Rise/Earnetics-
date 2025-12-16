export interface Objective {
    id: string;
    title: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    status: 'pending' | 'active' | 'completed' | 'archived';
    createdAt: number;
    tags: string[];
}

export interface Initiative {
    id: string;
    objectiveId: string;
    title: string;
    status: 'pending' | 'active' | 'completed' | 'blocked';
}

export interface Runbook {
    id: string;
    name: string;
    version: string;
    steps: RunStep[];
    inputSchema: Record<string, any>;
    outputSchema: Record<string, any>;
    policy: ScopePolicy;
}

export interface RunStep {
    id: string;
    runbookId: string;
    order: number;
    agentRole: string;
    toolCalls: string[]; // Tool names
    scopePolicy: ScopePolicy;
    requiresApproval: boolean;
}

export interface Task {
    id: string;
    objectiveId: string;
    deptId: string;
    title: string;
    status: 'todo' | 'in_progress' | 'review' | 'done';
    priority: 'low' | 'medium' | 'high';
    inputs: Record<string, any>;
    createdAt: number;
    updatedAt: number;
}

export interface Agent {
    id: string;
    deptId: string;
    name: string;
    role: string;
    state: 'idle' | 'working' | 'paused' | 'error';
    toolsAllowed: string[];
    lastHeartbeatAt: number;
}

export interface Artifact {
    id: string;
    taskId?: string;
    type: 'document' | 'code' | 'image' | 'data';
    title: string;
    uri: string;
    hash: string;
    createdBy: string;
    createdAt: number;
    provenance: ArtifactProvenance;
}

export interface ArtifactProvenance {
    eventIds: string[];
    inputs: Record<string, any>[];
    toolsUsed: string[];
    promptContext?: string;
    diffs?: string;
    approvals: string[]; // Approval IDs
}

export interface ApprovalRequest {
    id: string;
    actionType: string;
    payload: any;
    status: 'pending' | 'approved' | 'rejected';
    requestedBy: string;
    createdAt: number;
    resolvedAt?: number;
}

export interface ScopePolicy {
    fsPaths: string[];
    domains: string[];
    spendCap?: number;
    postMode?: 'auto' | 'review';
    accounts: string[];
}

export interface KPI {
    id: string;
    deptId: string;
    name: string;
    value: number;
    ts: number;
}

export interface AppEvent {
    id: string;
    type: string;
    payload: any;
    timestamp: number;
    meta?: any;
}
