import React, { useCallback, useEffect, useState, useMemo } from 'react';
import { API_BASE_URL } from '../../api/config';
import { Book, Search, ExternalLink, Brain, Briefcase, Scale, Zap, Users, TrendingUp, FileText, Globe } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';

interface KnowledgeItem {
  id: string;
  title: string;
  category: string;
  description: string;
  content?: string;
  tags?: string[];
  source?: string;
  url?: string;
}

interface AgentInfo {
  name: string;
  role: string;
  division: string;
  department: string;
  specialties: string[];
  personality: string;
  performance?: number;
  experience?: number;
}

type KnowledgeCategory = 'all' | 'agents' | 'revenue-strategies' | 'business-laws' | 'workflows' | 'external-resources';

export const KnowledgeLibrary: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<KnowledgeCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const { agents: agentStore } = useAgentStore();

  const loadKnowledge = useCallback(async () => {
    setLoading(true);
    try {
      // Load library items
      const libraryResponse = await fetch(`${API_BASE_URL}/api/library/`);
      if (libraryResponse.ok) {
        const libraryData = await libraryResponse.json();
        const items = (libraryData.items || []).map((item: any) => ({
          id: `library-${item.id}`,
          title: item.title,
          category: item.category || 'general',
          description: item.description || '',
          content: item.detailed_playbook || item.description,
          tags: typeof item.tags === 'string' ? JSON.parse(item.tags || '[]') : item.tags || [],
          source: item.created_by_agent || 'System',
        }));
        setKnowledgeItems(items);
      }

      // Load agent information
      const agentsResponse = await fetch(`${API_BASE_URL}/api/agents/roster`);
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        const agentInfos: AgentInfo[] = (agentsData.agents || []).map((agent: any) => ({
          name: agent.name,
          role: agent.role || '',
          division: agent.division || '',
          department: agent.department || '',
          specialties: agent.specialties || [],
          personality: agent.personality || '',
          performance: agent.performance_score,
          experience: agent.experience || 0,
        }));
        setAgents(agentInfos);
      }
    } catch (err) {
      console.error('Failed to load knowledge:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadKnowledge();
  }, [loadKnowledge]);

  // Build comprehensive knowledge base
  const allKnowledge = useMemo(() => {
    const items: KnowledgeItem[] = [...knowledgeItems];

    // Add agent information as knowledge items
    agents.forEach(agent => {
      items.push({
        id: `agent-${agent.name}`,
        title: `${agent.name} - ${agent.role}`,
        category: 'agents',
        description: agent.personality,
        content: `
**Division:** ${agent.division}
**Department:** ${agent.department}
**Role:** ${agent.role}
**Specialties:** ${agent.specialties.join(', ')}
**Performance Score:** ${agent.performance?.toFixed(1) || 'N/A'}
**Experience Level:** ${agent.experience || 0} actions

## Job Description
${agent.personality}

## Abilities
${agent.specialties.map(s => `- ${s}`).join('\n')}
        `,
        tags: ['agent', agent.division.toLowerCase(), agent.department.toLowerCase()],
        source: 'Agent Registry',
      });
    });

    // Add revenue strategies (core plays)
    items.push({
      id: 'revenue-strategy-1',
      title: 'Revenue Stream Strategies',
      category: 'revenue-strategies',
      description: 'Core revenue generation strategies and plays',
      content: `
## Core Revenue Strategies

### Product Sales
- Digital product creation and launch
- Payment gateway integration
- Landing page optimization
- Marketing campaign automation

### Affiliate Marketing
- Affiliate network management
- Commission tracking
- Link optimization
- Partner relationship management

### Email Marketing
- List building and segmentation
- Campaign automation
- A/B testing
- Conversion optimization

### Lead Generation
- Web scraping and data extraction
- Lead qualification
- List building
- CRM integration
      `,
      tags: ['revenue', 'strategy', 'core-plays'],
      source: 'Revenue Strategy Cell',
    });

    // Add business laws and compliance
    items.push({
      id: 'business-law-1',
      title: 'Business Laws & Compliance',
      category: 'business-laws',
      description: 'Essential business laws and compliance requirements',
      content: `
## Business Laws & Compliance

### Payment Processing
- PCI DSS compliance for payment handling
- Stripe Terms of Service
- PayPal Acceptable Use Policy
- Refund and chargeback policies

### Data Protection
- GDPR compliance for EU customers
- CCPA for California residents
- Data encryption requirements
- Privacy policy requirements

### Business Operations
- UCC filings for business protection
- Tax compliance and reporting
- Contract law basics
- Intellectual property protection

### Email Marketing Laws
- CAN-SPAM Act compliance
- Opt-in/opt-out requirements
- Unsubscribe mechanisms
- Sender identification
      `,
      tags: ['legal', 'compliance', 'business-law'],
      source: 'Legal & Sovereignty Department',
    });

    // Add workflow documentation
    items.push({
      id: 'workflow-1',
      title: 'Workflow Operations',
      category: 'workflows',
      description: 'Standard workflows and operational procedures',
      content: `
## Standard Workflows

### Product Launch Workflow
1. Product ideation and validation
2. Content creation and packaging
3. Payment link generation
4. Landing page creation
5. Marketing campaign launch
6. Sales tracking and optimization

### Lead Generation Workflow
1. Target website identification
2. Web scraping execution
3. Lead qualification
4. Email list building
5. Campaign segmentation
6. Nurture sequence setup

### Revenue Cycle Workflow
1. Opportunity discovery
2. Market validation
3. Product development
4. Launch preparation
5. Marketing activation
6. Performance monitoring
      `,
      tags: ['workflow', 'operations', 'process'],
      source: 'Corporate Execution',
    });

    // Add external research resources
    items.push({
      id: 'external-resource-1',
      title: 'Internet Archive',
      category: 'external-resources',
      description: 'Access to Internet Archive for research and information gathering',
      url: 'https://archive.org',
      content: `
## Internet Archive Access

The Internet Archive provides access to:
- Historical web pages
- Books and publications
- Audio and video content
- Software and media archives

**Access:** https://archive.org

Agents can use this resource to:
- Research historical trends
- Gather market intelligence
- Study competitor strategies
- Access archived documentation
      `,
      tags: ['research', 'external', 'archive'],
      source: 'System',
    });

    items.push({
      id: 'external-resource-2',
      title: 'Additional Research Resources',
      category: 'external-resources',
      description: 'Additional resources for agent research and learning',
      content: `
## Research Resources

### Academic & Research
- Google Scholar: https://scholar.google.com
- ResearchGate: https://www.researchgate.net
- arXiv: https://arxiv.org

### Business Intelligence
- Crunchbase: https://www.crunchbase.com
- SimilarWeb: https://www.similarweb.com
- SEMrush: https://www.semrush.com

### Market Research
- Statista: https://www.statista.com
- Pew Research: https://www.pewresearch.org
- Industry reports and whitepapers
      `,
      tags: ['research', 'external', 'intelligence'],
      source: 'System',
    });

    return items;
  }, [knowledgeItems, agents]);

  // Filter knowledge based on category and search
  const filteredKnowledge = useMemo(() => {
    let filtered = allKnowledge;

    if (activeCategory !== 'all') {
      filtered = filtered.filter(item => item.category === activeCategory);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.content?.toLowerCase().includes(query) ||
        item.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }

    return filtered;
  }, [allKnowledge, activeCategory, searchQuery]);

  const categories: Array<{ id: KnowledgeCategory; label: string; icon: React.ReactNode; count: number }> = [
    { id: 'all', label: 'All Knowledge', icon: <Book size={16} />, count: allKnowledge.length },
    { id: 'agents', label: 'Agents', icon: <Users size={16} />, count: agents.length },
    { id: 'revenue-strategies', label: 'Revenue Strategies', icon: <TrendingUp size={16} />, count: allKnowledge.filter(k => k.category === 'revenue-strategies').length },
    { id: 'business-laws', label: 'Business Laws', icon: <Scale size={16} />, count: allKnowledge.filter(k => k.category === 'business-laws').length },
    { id: 'workflows', label: 'Workflows', icon: <Zap size={16} />, count: allKnowledge.filter(k => k.category === 'workflows').length },
    { id: 'external-resources', label: 'External Resources', icon: <Globe size={16} />, count: allKnowledge.filter(k => k.category === 'external-resources').length },
  ];

  return (
    <div className="knowledge-library">
      <header className="panel-header">
        <div>
          <h3>📚 Central Knowledge Library</h3>
          <span className="text-xs text-slate-400">Comprehensive knowledge base for agents and operations</span>
        </div>
        <button
          type="button"
          className="refresh-button"
          onClick={() => void loadKnowledge()}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      <div className="knowledge-library__search">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-900/60 border border-slate-700/50 text-white placeholder-slate-500"
          />
        </div>
      </div>

      <div className="knowledge-library__categories">
        {categories.map(cat => (
          <button
            key={cat.id}
            type="button"
            onClick={() => setActiveCategory(cat.id)}
            className={`category-button ${activeCategory === cat.id ? 'active' : ''}`}
          >
            {cat.icon}
            <span>{cat.label}</span>
            <span className="badge">{cat.count}</span>
          </button>
        ))}
      </div>

      <div className="knowledge-library__content">
        {filteredKnowledge.length === 0 ? (
          <p className="panel-empty">No knowledge items found. Try adjusting your search or category.</p>
        ) : (
          <div className="knowledge-grid">
            {filteredKnowledge.map(item => (
              <div key={item.id} className="knowledge-card">
                <div className="knowledge-card__header">
                  <h4>{item.title}</h4>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="external-link-button"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
                <p className="knowledge-card__description">{item.description}</p>
                {item.content && (
                  <details className="knowledge-card__details">
                    <summary>View Details</summary>
                    <div className="knowledge-card__content">
                      <pre className="whitespace-pre-wrap text-xs">{item.content}</pre>
                    </div>
                  </details>
                )}
                <div className="knowledge-card__footer">
                  {item.tags && item.tags.length > 0 && (
                    <div className="tags">
                      {item.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                  )}
                  {item.source && (
                    <span className="text-xs text-slate-500">Source: {item.source}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
