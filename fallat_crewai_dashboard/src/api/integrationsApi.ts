/** API client for integration management. */

import { API_BASE_URL, getAuthHeaders } from './config';

export interface IntegrationStatus {
    status: 'connected' | 'disconnected';
    missing_vars: string[];
    found_in_vault?: string[];
    production_mode: boolean;
}

export interface IntegrationRequirements {
    integration: string;
    requirements: Array<{
        name: string;
        description: string;
        required: boolean;
    }>;
}

export interface IntegrationConfig {
    credentials: Record<string, string>;
    test_connection?: boolean;
}

export interface TestResult {
    success: boolean;
    message: string;
    details?: Record<string, any>;
}

export interface ConfigureResponse {
    status: string;
    integration: string;
    credentials_stored: string[];
    test_result?: TestResult;
}

/**
 * Get status of all integrations.
 */
export async function fetchIntegrationStatus(): Promise<Record<string, IntegrationStatus>> {
    const response = await fetch(`${API_BASE_URL || '/api'}/integrations/status`, {
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch integration status: ${response.statusText}`);
    }
    return await response.json();
}

/**
 * Get requirements for a specific integration.
 */
export async function fetchIntegrationRequirements(integrationName: string): Promise<IntegrationRequirements> {
    const response = await fetch(`${API_BASE_URL || '/api'}/integrations/${integrationName}/requirements`, {
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch requirements: ${response.statusText}`);
    }
    return await response.json();
}

/**
 * Configure an integration.
 */
export async function configureIntegration(
    integrationName: string,
    config: IntegrationConfig
): Promise<ConfigureResponse> {
    const response = await fetch(`${API_BASE_URL || '/api'}/integrations/${integrationName}/configure`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(config),
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `Failed to configure integration: ${response.statusText}`);
    }
    
    return await response.json();
}

/**
 * Test an integration connection.
 */
export async function testIntegration(integrationName: string): Promise<TestResult> {
    const response = await fetch(`${API_BASE_URL || '/api'}/integrations/${integrationName}/test`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `Failed to test integration: ${response.statusText}`);
    }
    
    return await response.json();
}

/**
 * Remove an integration (delete credentials from vault).
 */
export async function removeIntegration(integrationName: string): Promise<{ status: string; integration: string; credentials_deleted: number }> {
    const response = await fetch(`${API_BASE_URL || '/api'}/integrations/${integrationName}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `Failed to remove integration: ${response.statusText}`);
    }
    
    return await response.json();
}
