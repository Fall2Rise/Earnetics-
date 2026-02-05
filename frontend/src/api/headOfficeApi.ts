/**
 * Head Office API Client
 * API endpoints for Owner Ops OS
 */
import { API_BASE_URL } from './config';
import { fetchWithTimeout, retryRequest } from '../utils/apiHelpers';

const HEAD_OFFICE_BASE = `${API_BASE_URL}/api/head-office`;

// Types
export interface DecisionQueueItem {
  id: string;
  title: string;
  category: string;
  recommendation: string;
  upside: string;
  cost?: number;
  risk: string;
  reversibility: string;
  alternatives: string[];
  required_by: string;
  status: 'pending' | 'approved' | 'denied' | 'request_info';
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface Contract {
  id: string;
  title: string;
  party_name: string;
  counterparty: string;
  contract_type: string;
  status: string;
  version: number;
  file_path?: string;
  signed_date?: string;
  expiry_date?: string;
  value?: number;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface ContractScanResult {
  contract_id: string;
  risk_level: string;
  executive_summary: string;
  risk_map: Record<string, string>;
  missing_items_checklist: string[];
  redline_pack: Record<string, unknown>;
  negotiation_playbook: string;
  email_draft: string;
  scanned_at: string;
}

export interface TaxTask {
  id: string;
  title: string;
  description?: string;
  jurisdiction: string;
  filing_type: string;
  deadline: string;
  status: string;
  owner_agent_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  name: string;
  category: string;
  owner: string;
  criticality: string;
  description?: string;
  value?: number;
  last_reviewed_at?: string;
  next_review_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AssetAlert {
  id: string;
  asset_id: string;
  alert_type: string;
  message: string;
  severity: string;
  status: string;
  triggered_at: string;
  resolved_at?: string;
}

export interface LawLibraryEntry {
  id: string;
  title: string;
  jurisdiction: string;
  applicability_tags: string[];
  plain_english_summary: string;
  compliance_checklist: string[];
  risk_level: string;
  primary_sources_links: string[];
  category: string;
  created_at: string;
  updated_at: string;
}

export interface MasterAIAction {
  id: string;
  request: string;
  mode: string;
  permissions_checked: boolean;
  approval_required: boolean;
  approval_token_used?: string;
  two_step_confirmed: boolean;
  result_status: string;
  result_message: string;
  audit_log_link: string;
  actor: string;
  timestamp: string;
}

// Executive Launchpad
export async function fetchOwnerBrief() {
  return retryRequest(async () => {
    const response = await fetchWithTimeout(`${HEAD_OFFICE_BASE}/executive/brief`, {
      method: 'GET',
    }, 10000);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  });
}

export async function fetchTodayBoard() {
  return retryRequest(async () => {
    const response = await fetchWithTimeout(`${HEAD_OFFICE_BASE}/executive/today-board`, {
      method: 'GET',
    }, 10000);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  });
}

// Decision Queue
export async function fetchDecisions(status?: string): Promise<DecisionQueueItem[]> {
  return retryRequest(async () => {
    const url = status ? `${HEAD_OFFICE_BASE}/decisions?status=${status}` : `${HEAD_OFFICE_BASE}/decisions`;
    const response = await fetchWithTimeout(url, {
      method: 'GET',
    }, 10000);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return data.decisions || data.items || [];
  });
}

export async function getDecision(id: string): Promise<DecisionQueueItem> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/decisions/${id}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function approveDecision(id: string): Promise<DecisionQueueItem> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/decisions/${id}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function denyDecision(id: string, reason?: string): Promise<DecisionQueueItem> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/decisions/${id}/deny`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Legal + Contracts
export async function fetchContracts(): Promise<Contract[]> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/legal/contracts`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return data.contracts || [];
}

export async function getContract(id: string): Promise<Contract> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/legal/contracts/${id}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function scanContract(contractId: string, contractText?: string): Promise<ContractScanResult> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/legal/contracts/${contractId}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ contract_text: contractText }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function getSignatureRecommendation(contractId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/legal/contracts/${contractId}/signature`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Tax Desk
export async function fetchTaxTasks(): Promise<TaxTask[]> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/tax/tasks`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return data.tasks || [];
}

export async function fetchTaxCalendar(): Promise<Record<string, unknown>> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/tax/calendar`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Assets + Safety Radar
export async function fetchAssets(): Promise<Asset[]> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/assets/inventory`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return data.assets || [];
}

export async function fetchAssetAlerts(): Promise<AssetAlert[]> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/assets/alerts`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return data.alerts || [];
}

// Law Library
export async function fetchLawEntries(category?: string): Promise<LawLibraryEntry[]> {
  const url = category ? `${HEAD_OFFICE_BASE}/law-library?category=${category}` : `${HEAD_OFFICE_BASE}/law-library`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return data.entries || [];
}

export async function getLawEntry(id: string): Promise<LawLibraryEntry> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/law-library/${id}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Master AI
export async function fetchMasterAIStatus(): Promise<Record<string, unknown>> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/master-ai/status`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function submitMasterAIRequest(request: string, mode: string): Promise<MasterAIAction> {
  const response = await fetch(`${HEAD_OFFICE_BASE}/master-ai/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request, mode }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
