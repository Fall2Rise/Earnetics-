/**
 * Intelligence Department API
 */
import { API_BASE_URL } from './config';

async function apiRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  const fullUrl = API_BASE_URL ? `${API_BASE_URL}${url}` : url;
  const response = await fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }
  return response.json();
}

export interface Signal {
  id: string;
  headline: string;
  topic: string;
  why_it_matters: string;
  actionable_angle: string;
  priority: number;
  created_at: string;
  citations: Array<{
    source_id: string;
    url: string;
    retrieved_at: string;
  }>;
}

export interface TruthLibraryAsset {
  asset_id: string;
  type: string;
  title: string;
  status: string;
  version: number;
  last_verified_at?: string;
  citations: any[];
  confidence: number;
  owner: string;
  tags: string[];
  content: any;
  measurable_results?: any;
  created_at: string;
  updated_at: string;
}

export interface LeadRecord {
  lead_id: string;
  entity_type: string;
  name: string;
  business_name?: string;
  role?: string;
  emails: Array<{ value: string; verified: boolean; type: string }>;
  phones: Array<{ value: string; verified: boolean; type: string }>;
  compliance: {
    legal_basis: string;
    consent: Record<string, string>;
    allowed_channels: string[];
    do_not_contact: boolean;
  };
  tags: string[];
  scores: Record<string, number>;
  created_at: string;
}

export interface DecisionPacket {
  packet_id: string;
  opportunity_id: string;
  generated_at: string;
  opportunity: {
    niche: string;
    offer_type: string;
    hypothesis: string;
    expected_roi: number;
    time_to_first_dollar: number;
  };
  why_now: {
    signals: any[];
    citations: any[];
  };
  status: string;
}

export interface Opportunity {
  opportunity_id: string;
  niche: string;
  offer_type: string;
  hypothesis: string;
  target: string;
  expected_roi: number;
  time_to_first_dollar: number;
  status: string;
  created_at: string;
}

export interface Experiment {
  asset_id: string;
  title: string;
  status: string;
  content: {
    hypothesis: string;
    setup: any;
    results?: any;
    conclusion?: string;
  };
  created_at: string;
}

export async function getSignals(limit = 20, priorityMin = 1, abortSignal?: AbortSignal): Promise<{ signals: Signal[]; total: number }> {
  return apiRequest<{ signals: Signal[]; total: number }>(
    `/api/intelligence/signals?limit=${limit}&priority_min=${priorityMin}`,
    { signal: abortSignal }
  );
}

export async function listTruthLibrary(
  query?: string,
  assetType?: string,
  status?: string,
  limit = 50,
  abortSignal?: AbortSignal
): Promise<{ assets: TruthLibraryAsset[]; total: number }> {
  const params = new URLSearchParams();
  if (query) params.append('query', query);
  if (assetType) params.append('asset_type', assetType);
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  
  return apiRequest<{ assets: TruthLibraryAsset[]; total: number }>(
    `/api/intelligence/truth-library?${params.toString()}`,
    { signal: abortSignal }
  );
}

export async function getTruthAsset(assetId: string, version?: number, abortSignal?: AbortSignal): Promise<TruthLibraryAsset> {
  const params = new URLSearchParams();
  if (version) params.append('version', version.toString());
  
  return apiRequest<TruthLibraryAsset>(
    `/api/intelligence/truth-library/${assetId}?${params.toString()}`,
    { signal: abortSignal }
  );
}

export async function listLeads(
  entityType?: string,
  tags?: string,
  limit = 100,
  abortSignal?: AbortSignal
): Promise<{ leads: LeadRecord[]; total: number }> {
  const params = new URLSearchParams();
  if (entityType) params.append('entity_type', entityType);
  if (tags) params.append('tags', tags);
  params.append('limit', limit.toString());
  
  return apiRequest<{ leads: LeadRecord[]; total: number }>(
    `/api/intelligence/lead-vault?${params.toString()}`,
    { signal: abortSignal }
  );
}

export async function getExecutiveInbox(status?: string, limit = 20, abortSignal?: AbortSignal): Promise<{
  packets: DecisionPacket[];
  total: number;
  pending: number;
  approved: number;
  rejected: number;
}> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  
  return apiRequest(`/api/intelligence/executive-inbox?${params.toString()}`, { signal: abortSignal });
}

export async function submitDecisionPacket(packet: DecisionPacket, abortSignal?: AbortSignal): Promise<{ success: boolean; packet_id: string }> {
  return apiRequest<{ success: boolean; packet_id: string }>(
    '/api/intelligence/executive-inbox/submit',
    {
      method: 'POST',
      body: JSON.stringify(packet),
      signal: abortSignal,
    }
  );
}

export async function decideOnPacket(
  packetId: string,
  decision: 'deploy' | 'experiment' | 'reject' | 'needs_evidence',
  note?: string,
  abortSignal?: AbortSignal
): Promise<{ success: boolean; decision: string }> {
  return apiRequest<{ success: boolean; decision: string }>(
    '/api/intelligence/executive-inbox/decide',
    {
      method: 'POST',
      body: JSON.stringify({ packet_id: packetId, decision, note }),
      signal: abortSignal,
    }
  );
}

export async function getOpportunityBacklog(abortSignal?: AbortSignal): Promise<{
  columns: {
    intake: Opportunity[];
    triage: Opportunity[];
    synthesis: Opportunity[];
    experiment: Opportunity[];
    validated: Opportunity[];
    sent_to_exec: Opportunity[];
    deployed: Opportunity[];
  };
}> {
  return apiRequest<{
    columns: {
      intake: Opportunity[];
      triage: Opportunity[];
      synthesis: Opportunity[];
      experiment: Opportunity[];
      validated: Opportunity[];
      sent_to_exec: Opportunity[];
      deployed: Opportunity[];
    };
  }>('/api/intelligence/opportunity-backlog', { signal: abortSignal });
}

export async function moveOpportunity(
  opportunityId: string,
  newStatus: string,
  abortSignal?: AbortSignal
): Promise<{ success: boolean; opportunity_id: string; status: string }> {
  return apiRequest(
    '/api/intelligence/opportunity-backlog/move',
    {
      method: 'POST',
      body: JSON.stringify({ opportunity_id: opportunityId, new_status: newStatus }),
      signal: abortSignal,
    }
  );
}

export async function listExperiments(status?: string, limit = 20, abortSignal?: AbortSignal): Promise<{
  experiments: Experiment[];
  total: number;
}> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  
  return apiRequest<{ experiments: Experiment[]; total: number }>(
    `/api/intelligence/experiments?${params.toString()}`,
    { signal: abortSignal }
  );
}

export async function getCampaignMetrics(campaignId: string, abortSignal?: AbortSignal): Promise<{
  campaign_id: string;
  traffic_clicks: number;
  leads_optin: number;
  conversions_purchase: number;
  revenue_recorded: number;
  emails_sent: number;
  emails_reply: number;
  emails_unsubscribe: number;
}> {
  return apiRequest(`/api/intelligence/campaigns/${campaignId}/metrics`, { signal: abortSignal });
}
