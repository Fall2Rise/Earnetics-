import { API_BASE_URL } from './config';

export interface ScrapedLead {
  id: number;
  email: string;
  name?: string;
  website?: string;
  source_url: string;
  source_domain: string;
  context?: string;
  qualified: number;
  added_to_list: number;
  created_at: string;
  updated_at: string;
}

export interface MarketingRecipient {
  email: string;
  campaign_id: number;
  sent_at: string;
  event_type: string;
  campaign_subject?: string;
  campaign_name?: string;
}

export interface Subscriber {
  id: number;
  email: string;
  first_name?: string;
  status: string;
  tags: string[];
  source?: string;
  created_at: string;
  updated_at: string;
}

export const leadManagementApi = {
  // Scraped Leads
  async getScrapedLeads(params?: {
    limit?: number;
    qualified_only?: boolean;
    added_to_list?: boolean;
    source_domain?: string;
  }): Promise<{ leads: ScrapedLead[]; total: number; qualified_count: number; added_to_list_count: number }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.qualified_only) queryParams.append('qualified_only', 'true');
    if (params?.added_to_list !== undefined) queryParams.append('added_to_list', params.added_to_list.toString());
    if (params?.source_domain) queryParams.append('source_domain', params.source_domain);

    const response = await fetch(`${API_BASE_URL}/api/leads/scraped?${queryParams}`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch scraped leads');
    return response.json();
  },

  async getScrapedLeadsStats(): Promise<{
    total_leads: number;
    qualified_leads: number;
    added_to_list: number;
    by_domain: Record<string, { total: number; qualified: number; added: number }>;
  }> {
    const response = await fetch(`${API_BASE_URL}/api/leads/scraped/stats`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch scraped leads stats');
    return response.json();
  },

  async qualifyLead(leadId: number, qualified: boolean = true): Promise<{ status: string; lead_id: number; qualified: boolean }> {
    const response = await fetch(`${API_BASE_URL}/api/leads/scraped/${leadId}/qualify?qualified=${qualified}`, {
      method: 'POST',
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to qualify lead');
    return response.json();
  },

  // Marketing Recipients
  async getMarketingRecipients(params?: {
    limit?: number;
    campaign_id?: number;
  }): Promise<{ recipients: MarketingRecipient[]; total: number; unique_emails: number }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.campaign_id) queryParams.append('campaign_id', params.campaign_id.toString());

    const response = await fetch(`${API_BASE_URL}/api/leads/marketing/recipients?${queryParams}`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch marketing recipients');
    return response.json();
  },

  async getMarketingRecipientsStats(): Promise<{
    total_campaigns: number;
    campaign_stats: Array<{ campaign_id: number; unique_recipients: number; total_sent: number }>;
    engagement: Record<string, { unique_count: number; total_count: number }>;
    total_sent: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/api/leads/marketing/recipients/stats`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch marketing recipients stats');
    return response.json();
  },

  // Subscribers
  async getSubscribers(params?: {
    limit?: number;
    status?: string;
    source?: string;
    tag?: string;
  }): Promise<{
    subscribers: Subscriber[];
    total: number;
    by_category: Record<string, number>;
    categories: Record<string, Subscriber[]>;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.source) queryParams.append('source', params.source);
    if (params?.tag) queryParams.append('tag', params.tag);

    const response = await fetch(`${API_BASE_URL}/api/leads/subscribers?${queryParams}`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch subscribers');
    return response.json();
  },

  async getSubscribersStats(): Promise<{
    total_subscribers: number;
    by_status: Record<string, number>;
    by_source: Record<string, number>;
    by_tag: Record<string, number>;
    active_count: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/api/leads/subscribers/stats`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch subscribers stats');
    return response.json();
  },
};
