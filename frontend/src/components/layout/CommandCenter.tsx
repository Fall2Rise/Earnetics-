import React, { useMemo, useState, useEffect } from 'react';
import { MessageSquare, User } from 'lucide-react';
import { NextStepAdvisor } from '../dashboard/NextStepAdvisor';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';
import { getMetrics, MetricsResult } from '../../api/metricsApi';
import { AgentsPanel } from '../dashboard/AgentsPanel';
import { AgentNexusPanel } from '../dashboard/AgentNexusPanel';
import { AgentDnaRegistryPanel } from '../dashboard/AgentDnaRegistryPanel';
import { ChainOfIntentTracerPanel } from '../dashboard/ChainOfIntentTracerPanel';
import { ContentEnginePanel } from '../dashboard/ContentEnginePanel';
import { ContentRegistryPanel } from '../dashboard/ContentRegistryPanel';
import { CredentialVaultPanel } from '../dashboard/CredentialVaultPanel';
import { DeadAgentProtocolPanel } from '../dashboard/DeadAgentProtocolPanel';
import { DirectiveCorePanel } from '../dashboard/DirectiveCorePanel';
import { EvolutionChamberPanel } from '../dashboard/EvolutionChamberPanel';
import { FallatSealPanel } from '../dashboard/FallatSealPanel';
import { ForecastEnginePanel } from '../dashboard/ForecastEnginePanel';
import { IntelligencePanel } from '../dashboard/IntelligencePanel';
import { KnowledgeVaultPanel } from '../dashboard/KnowledgeVaultPanel';
import { LegalComplianceMonitorPanel } from '../dashboard/LegalComplianceMonitorPanel';
import { IntegrationRegistryPanel } from '../dashboard/IntegrationRegistryPanel';
import { MissionControlPanel } from '../dashboard/MissionControlPanel';
import { ObserverProtocolPanel } from '../dashboard/ObserverProtocolPanel';
import { PlaybookLibraryPanel } from '../dashboard/PlaybookLibraryPanel';
import { QuantumSuccessionPanel } from '../dashboard/QuantumSuccessionPanel';
import { SignalDashboard } from '../dashboard/SignalDashboard';
import { SimulationEnginePanel } from '../dashboard/SimulationEnginePanel';
import { ToolForgePanel } from '../dashboard/ToolForgePanel';
import { ServicesStatusPanel } from '../dashboard/ServicesStatusPanel';
import { Web3DepartmentPanel } from '../dashboard/Web3DepartmentPanel';
import { LockedModulePanel } from '../dashboard/LockedModulePanel';
import { TruthLibraryBrowser } from '../dashboard/TruthLibraryBrowser';
import { LeadVaultBrowser } from '../dashboard/LeadVaultBrowser';
import { ExecutiveInbox } from '../dashboard/ExecutiveInbox';
import { OpportunityBacklogKanban } from '../dashboard/OpportunityBacklogKanban';
import { ExperimentsLab } from '../dashboard/ExperimentsLab';
import { CommandRoom } from '../../scenes/CommandRoom';
import { OperationsPulse } from '../dashboard/OperationsPulse';
import { PerformanceMetrics } from '../dashboard/PerformanceMetrics';
import { SchedulerPanel } from '../workflows/SchedulerPanel';
import { AuditLogPanel } from '../workflows/AuditLogPanel';
import { CredentialManager } from '../workflows/CredentialManager';
import { ApprovalCenter } from '../workflows/ApprovalCenter';
import { NotificationsPanel } from '../workflows/NotificationsPanel';
import { AgentManager } from '../agents/AgentManager';
import { FinancialDashboard } from '../dashboard/FinancialDashboard';
import { IntegrationsPanel } from '../dashboard/IntegrationsPanel';
import { EvolutionView } from '../dashboard/EvolutionView';
import { SecurityPanel } from '../dashboard/SecurityPanel';
import { RealTimeLogViewer } from '../dashboard/RealTimeLogViewer';
import { LeadManagementPanel } from '../dashboard/LeadManagementPanel';
import { MarketingRecipientsPanel } from '../dashboard/MarketingRecipientsPanel';
import { SubscribersPanel } from '../dashboard/SubscribersPanel';
import { IntelligenceRecommendations } from '../dashboard/IntelligenceRecommendations';
import { PerformanceBottlenecks } from '../dashboard/PerformanceBottlenecks';
import { KnowledgeLibrary } from '../dashboard/KnowledgeLibrary';
import { ExecutiveLaunchpad } from '../dashboard/ExecutiveLaunchpad';
import { DecisionQueuePanel } from '../dashboard/DecisionQueuePanel';
import { LegalContractsPanel } from '../dashboard/LegalContractsPanel';
import { TaxDeskPanel } from '../dashboard/TaxDeskPanel';
import { AssetsSafetyPanel } from '../dashboard/AssetsSafetyPanel';
import { LawLibraryPanel } from '../dashboard/LawLibraryPanel';
import { MasterAIPanel } from '../dashboard/MasterAIPanel';
import { DashboardControls } from '../dashboard/DashboardControls';
import { WorkflowMonitorPanel } from '../dashboard/WorkflowMonitorPanel';
import { ReasonExplainEnginePanel } from '../dashboard/ReasonExplainEnginePanel';
import { ResourceMonitorPanel } from '../dashboard/ResourceMonitorPanel';

type CommandSection =
  | 'overview'
  | 'directive-core'
  | 'workflow-monitor'
  | 'agent-nexus'
  | 'resource-monitor'
  | 'mission-control'
  | 'reason-explain'
  | 'chain-intent'
  | 'evolution-chamber'
  | 'simulation-engine'
  | 'forecast-engine'
  | 'observer-protocol'
  | 'dead-agent-protocol'
  | 'quantum-succession'
  | 'playbook-library'
  | 'tool-forge'
  | 'knowledge-vault'
  | 'content-registry'
  | 'credential-vault'
  | 'legal-compliance'
  | 'agent-dna'
  | 'integration-registry'
  | 'services-registry'
  | 'content-engine'
  | 'web3-department'
  | 'fallat-seal'
  | 'synthetic-identity'
  | 'narrative-influence'
  | 'global-intelligence'
  | 'ai-legal-engine'
  | 'blackbox-shadow-log'
  | 'agents'
  | 'workflows'
  | 'intelligence'
  | 'financial'
  | 'security'
  | 'leads'
  | 'marketing'
  | 'subscribers'
  | 'head-office';

// Navigation Categories
type NavCategory = 'Operations' | 'Intelligence' | 'Assets' | 'Governance' | 'Agents' | 'Financial' | 'Security' | 'Restricted';

interface NavGroup {
  category: NavCategory;
  items: { key: string; label: string }[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    category: 'Operations',
    items: [
      { key: 'overview', label: 'Overview' },
      { key: 'mission-control', label: 'Mission Control' },
      { key: 'workflow-monitor', label: 'Workflows' },
      { key: 'resource-monitor', label: 'Resources' },
      { key: 'workflows', label: 'Tasks' }, // Reusing workflows render
    ]
  },
  {
    category: 'Intelligence',
    items: [
      { key: 'intelligence', label: 'Dashboard' },
      { key: 'leads', label: 'Leads' },
      { key: 'knowledge-vault', label: 'Knowledge Vault' },
      { key: 'chain-intent', label: 'Chain of Intent' },
      { key: 'reason-explain', label: 'Reasoning' },
      { key: 'simulation-engine', label: 'Simulator' },
    ]
  },
  {
    category: 'Assets',
    items: [
      { key: 'content-engine', label: 'Content Engine' },
      { key: 'content-registry', label: 'Registry' },
      { key: 'tool-forge', label: 'Tool Forge' },
      { key: 'playbook-library', label: 'Playbooks' },
      { key: 'services-registry', label: 'Services' },
      { key: 'integration-registry', label: 'Integrations' },
    ]
  },
  {
    category: 'Agents',
    items: [
      { key: 'agents', label: 'Roster' },
      { key: 'agent-nexus', label: 'Nexus' },
      { key: 'agent-dna', label: 'DNA' },
      { key: 'dead-agent-protocol', label: 'Protocols' },
      { key: 'quantum-succession', label: 'Succession' },
    ]
  },
  {
    category: 'Financial',
    items: [
      { key: 'financial', label: 'Finance' },
      { key: 'forecast-engine', label: 'Forecasts' },
      { key: 'marketing', label: 'Marketing' },
      { key: 'subscribers', label: 'Subscribers' },
      { key: 'web3-department', label: 'Web3' },
    ]
  },
  {
    category: 'Governance',
    items: [
      { key: 'head-office', label: 'Head Office' },
      { key: 'directive-core', label: 'Directive Core' },
      { key: 'evolution-chamber', label: 'Evolution' },
      { key: 'legal-compliance', label: 'Compliance' },
    ]
  },
  {
    category: 'Security',
    items: [
      { key: 'security', label: 'Security' },
      { key: 'credential-vault', label: 'Vault' },
      { key: 'fallat-seal', label: 'Seal' },
      { key: 'observer-protocol', label: 'Observer' },
    ]
  },
  {
    category: 'Restricted',
    items: [
      { key: 'synthetic-identity', label: 'Identity Swarm' },
      { key: 'narrative-influence', label: 'Influence' },
      { key: 'global-intelligence', label: 'Global Intel' },
      { key: 'ai-legal-engine', label: 'Legal Engine' },
      { key: 'blackbox-shadow-log', label: 'Blackbox' },
    ]
  }
];


const renderOverview = () => (
  <div className="panel-stack">
    <div className="command-panel command-panel--visual">
      <CommandRoom />
    </div>
    <div className="command-panel">
      <OperationsPulse />
    </div>
    <div className="command-panel">
      <PerformanceMetrics />
    </div>
    <div className="command-panel">
      <DashboardControls />
    </div>
  </div>
);

const renderDirectiveCore = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <DirectiveCorePanel />
    </div>
    <div className="command-panel">
      <AuditLogPanel />
    </div>
  </div>
);

const renderWorkflowMonitor = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <WorkflowMonitorPanel />
    </div>
    <div className="command-panel">
      <SchedulerPanel />
    </div>
    <div className="command-panel">
      <ApprovalCenter />
    </div>
  </div>
);

const renderAgentNexus = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <AgentNexusPanel />
    </div>
    <div className="command-panel">
      <AgentsPanel />
    </div>
    <div className="command-panel">
      <AgentManager />
    </div>
  </div>
);

const renderResourceMonitor = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ResourceMonitorPanel />
    </div>
  </div>
);

const renderMissionControl = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <MissionControlPanel />
    </div>
    <div className="command-panel">
      <OperationsPulse />
    </div>
  </div>
);

const renderReasonExplain = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ReasonExplainEnginePanel />
    </div>
  </div>
);

const renderChainIntent = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ChainOfIntentTracerPanel />
    </div>
  </div>
);

const renderEvolutionChamber = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <EvolutionChamberPanel />
    </div>
    <div className="command-panel">
      <EvolutionView />
    </div>
  </div>
);

const renderSimulationEngine = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <SimulationEnginePanel />
    </div>
  </div>
);

const renderForecastEngine = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ForecastEnginePanel />
    </div>
  </div>
);

const renderObserverProtocol = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ObserverProtocolPanel />
    </div>
  </div>
);

const renderDeadAgentProtocol = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <DeadAgentProtocolPanel />
    </div>
  </div>
);

const renderQuantumSuccession = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <QuantumSuccessionPanel />
    </div>
  </div>
);

const renderPlaybookLibrary = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <PlaybookLibraryPanel />
    </div>
  </div>
);

const renderToolForge = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ToolForgePanel />
    </div>
  </div>
);

const renderKnowledgeVault = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <KnowledgeVaultPanel />
    </div>
  </div>
);

const renderContentRegistry = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ContentRegistryPanel />
    </div>
  </div>
);

const renderCredentialVault = () => (
  <div className="panel-stack">
    <CredentialVaultPanel />
  </div>
);

const renderLegalCompliance = () => (
  <div className="panel-stack">
    <LegalComplianceMonitorPanel />
  </div>
);

const renderAgentDnaRegistry = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <AgentDnaRegistryPanel />
    </div>
  </div>
);

const renderIntegrationRegistry = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <IntegrationRegistryPanel />
    </div>
  </div>
);

const renderServicesRegistry = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ServicesStatusPanel />
    </div>
  </div>
);

const renderContentEngine = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ContentEnginePanel />
    </div>
  </div>
);

const renderWeb3Department = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <Web3DepartmentPanel />
    </div>
  </div>
);

const renderFallatSeal = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <FallatSealPanel />
    </div>
  </div>
);

const renderSyntheticIdentity = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LockedModulePanel
        title="Synthetic Identity Swarm"
        description="Persona generation and identity management (locked)."
        action="synthetic_identity_swarm_request"
        directiveRef="avoid_deception_or_manipulation"
      />
    </div>
  </div>
);

const renderNarrativeInfluence = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LockedModulePanel
        title="Narrative Influence Engine"
        description="Public narrative shaping (locked)."
        action="narrative_influence_engine_request"
        directiveRef="avoid_deception_or_manipulation"
      />
    </div>
  </div>
);

const renderGlobalIntelligence = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LockedModulePanel
        title="Global Intelligence Grid"
        description="Aggregated intel fusion (locked)."
        action="global_intelligence_grid_request"
        directiveRef="respect_lawful_boundaries"
      />
    </div>
  </div>
);

const renderAiLegalEngine = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LockedModulePanel
        title="AI Legal Engine"
        description="Legal action drafting and defense (locked)."
        action="ai_legal_engine_request"
        directiveRef="respect_lawful_boundaries"
      />
    </div>
  </div>
);

const renderBlackboxShadowLog = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LockedModulePanel
        title="Blackbox Shadow Log"
        description="Hidden forensic ledger (locked)."
        action="blackbox_shadow_log_request"
        directiveRef="auditability"
      />
    </div>
  </div>
);

const renderAgents = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <AgentsPanel />
    </div>
    <div className="command-panel">
      <AgentManager />
    </div>
    <div className="command-panel">
      <OperationsPulse compact />
    </div>
  </div>
);

const renderWorkflows = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <OperationsPulse enableAutonomyControls />
    </div>
    <div className="command-panel">
      <SchedulerPanel />
    </div>
    <div className="command-panel">
      <ApprovalCenter />
    </div>
    <div className="command-panel">
      <NotificationsPanel />
    </div>
    <div className="command-panel">
      <CredentialManager />
    </div>
    <div className="command-panel">
      <AuditLogPanel />
    </div>
  </div>
);

const renderIntelligence = () => (
  <div className="panel-stack">
    <div className="command-panel command-panel--visual">
      <Office3DView />
    </div>
    <div className="command-panel">
      <EvolutionView />
    </div>
    <div className="command-panel command-panel--full">
      <SignalDashboard />
    </div>
    <div className="command-panel command-panel--full">
      <TruthLibraryBrowser />
    </div>
    <div className="command-panel command-panel--full">
      <LeadVaultBrowser />
    </div>
    <div className="command-panel command-panel--full">
      <ExecutiveInbox />
    </div>
    <div className="command-panel command-panel--full">
      <OpportunityBacklogKanban />
    </div>
    <div className="command-panel command-panel--full">
      <ExperimentsLab />
    </div>
    <div className="command-panel">
      <IntelligencePanel />
    </div>
    <div className="command-panel command-panel--large">
      <KnowledgeLibrary />
    </div>
    <div className="command-panel">
      <IntelligenceRecommendations />
    </div>
    <div className="command-panel">
      <PerformanceBottlenecks />
    </div>
  </div>
);

const renderFinancial = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <FinancialDashboard />
    </div>
    <div className="command-panel">
      <IntegrationsPanel />
    </div>
    <div className="command-panel">
      <OperationsPulse compact />
    </div>
  </div>
);

const renderSecurity = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <SecurityPanel />
    </div>
    <div className="command-panel">
      <OperationsPulse compact />
    </div>
  </div>
);

const renderLeads = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <LeadManagementPanel />
    </div>
  </div>
);

const renderMarketing = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <MarketingRecipientsPanel />
    </div>
  </div>
);

const renderSubscribers = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <SubscribersPanel />
    </div>
  </div>
);

const renderHeadOffice = () => (
  <div className="panel-stack">
    <div className="command-panel">
      <ExecutiveLaunchpad />
    </div>
    <div className="command-panel command-panel--full">
      <DecisionQueuePanel />
    </div>
    <div className="command-panel command-panel--full">
      <LegalContractsPanel />
    </div>
    <div className="command-panel command-panel--full">
      <TaxDeskPanel />
    </div>
    <div className="command-panel command-panel--full">
      <AssetsSafetyPanel />
    </div>
    <div className="command-panel command-panel--full">
      <LawLibraryPanel />
    </div>
    <div className="command-panel command-panel--full">
      <MasterAIPanel />
    </div>
  </div>
);

export const CommandCenter: React.FC = () => {
  const [activeSection, setActiveSection] = useState<CommandSection>('overview');
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [metrics, setMetrics] = useState<MetricsResult | null>(null);

  // Load status and metrics for the advisor
  useEffect(() => {
    const loadData = async () => {
      try {
        const [statusData, metricsData] = await Promise.all([
          fetchSystemStatus(),
          getMetrics()
        ]);
        setStatus(statusData);
        setMetrics(metricsData);
      } catch (e) {
        // Silent fail
      }
    };
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Listen for tab switch events from advisor
  useEffect(() => {
    const handleSwitch = (e: CustomEvent) => {
        if (e.detail) setActiveSection(e.detail as CommandSection);
    };
    window.addEventListener('switch-tab', handleSwitch as EventListener);
    return () => window.removeEventListener('switch-tab', handleSwitch as EventListener);
  }, []);

  const sections = useMemo(
    () => [
      { key: 'overview', label: 'Command Center', render: renderOverview },
      { key: 'directive-core', label: 'Directive Core', render: renderDirectiveCore },
      { key: 'workflow-monitor', label: 'Workflow Monitor', render: renderWorkflowMonitor },
      { key: 'agent-nexus', label: 'Agent Nexus', render: renderAgentNexus },
      { key: 'resource-monitor', label: 'Resource Monitor', render: renderResourceMonitor },
      { key: 'mission-control', label: 'Mission Control', render: renderMissionControl },
      { key: 'reason-explain', label: 'Reason Explain', render: renderReasonExplain },
      { key: 'chain-intent', label: 'Chain of Intent', render: renderChainIntent },
      { key: 'evolution-chamber', label: 'Evolution Chamber', render: renderEvolutionChamber },
      { key: 'simulation-engine', label: 'Simulation Engine', render: renderSimulationEngine },
      { key: 'forecast-engine', label: 'Forecast Engine', render: renderForecastEngine },
      { key: 'observer-protocol', label: 'Observer Protocol', render: renderObserverProtocol },
      { key: 'dead-agent-protocol', label: 'Dead Agent Protocol', render: renderDeadAgentProtocol },
      { key: 'quantum-succession', label: 'Quantum Succession', render: renderQuantumSuccession },
      { key: 'playbook-library', label: 'Playbook Library', render: renderPlaybookLibrary },
      { key: 'tool-forge', label: 'Tool Forge', render: renderToolForge },
      { key: 'knowledge-vault', label: 'Knowledge Vault', render: renderKnowledgeVault },
      { key: 'content-registry', label: 'Content Registry', render: renderContentRegistry },
      { key: 'credential-vault', label: 'Credential Vault', render: renderCredentialVault },
      { key: 'legal-compliance', label: 'Legal Compliance', render: renderLegalCompliance },
      { key: 'agent-dna', label: 'Agent DNA Registry', render: renderAgentDnaRegistry },
      { key: 'integration-registry', label: 'Integration Registry', render: renderIntegrationRegistry },
      { key: 'services-registry', label: 'Service Registry', render: renderServicesRegistry },
      { key: 'content-engine', label: 'Content Engine', render: renderContentEngine },
      { key: 'web3-department', label: 'Web3 Department', render: renderWeb3Department },
      { key: 'fallat-seal', label: 'Fallat Seal', render: renderFallatSeal },
      { key: 'synthetic-identity', label: 'Synthetic Identity', render: renderSyntheticIdentity },
      { key: 'narrative-influence', label: 'Narrative Influence', render: renderNarrativeInfluence },
      { key: 'global-intelligence', label: 'Global Intelligence', render: renderGlobalIntelligence },
      { key: 'ai-legal-engine', label: 'AI Legal Engine', render: renderAiLegalEngine },
      { key: 'blackbox-shadow-log', label: 'Blackbox Shadow Log', render: renderBlackboxShadowLog },
      { key: 'agents', label: 'Agents', render: renderAgents },
      { key: 'workflows', label: 'Workflows', render: renderWorkflows },
      { key: 'intelligence', label: 'Intelligence', render: renderIntelligence },
      { key: 'financial', label: 'Financial', render: renderFinancial },
      { key: 'security', label: 'Security', render: renderSecurity },
      { key: 'leads', label: 'Leads', render: renderLeads },
      { key: 'marketing', label: 'Marketing', render: renderMarketing },
      { key: 'subscribers', label: 'Subscribers', render: renderSubscribers },
      { key: 'head-office', label: 'Head Office', render: renderHeadOffice },
    ],
    []
  );

  const section = sections.find((item) => item.key === activeSection) ?? sections[0];

  // Find the active category label
  const activeCategory = NAV_GROUPS.find(g => g.items.some(i => i.key === activeSection))?.category;

  return (
    <>
      <section className="command-center" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <div className="command-center__nav" style={{ flexShrink: 0, padding: '0.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          
          {/* Top Level Categories */}
          <div className="flex flex-wrap gap-2 pb-2">
             {NAV_GROUPS.map(group => {
                 const isActiveGroup = group.items.some(item => item.key === activeSection);
                 return (
                     <div key={group.category} className={`flex flex-col gap-1 p-1 rounded-xl transition-colors ${isActiveGroup ? 'bg-white/5 border border-white/10' : 'hover:bg-white/5'}`}>
                         <div className="px-2 text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">
                             {group.category}
                         </div>
                         <div className="flex gap-1">
                             {group.items.map(item => (
                                 <button
                                    key={item.key}
                                    type="button"
                                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                                        activeSection === item.key 
                                        ? 'bg-cyan-500/20 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.2)] border border-cyan-500/30' 
                                        : 'text-slate-400 hover:text-white hover:bg-white/10'
                                    }`}
                                    onClick={() => setActiveSection(item.key as CommandSection)}
                                 >
                                     {item.label}
                                 </button>
                             ))}
                         </div>
                     </div>
                 );
             })}
          </div>

        </div>
        
        {/* Page Header / Breadcrumb */}
        <div className="px-6 py-2 border-b border-white/5 bg-black/20 backdrop-blur-sm flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
                <span className="text-slate-500 font-medium uppercase tracking-wider">{activeCategory}</span>
                <span className="text-slate-600">/</span>
                <span className="text-cyan-400 font-bold tracking-wide">{section.label}</span>
            </div>

            <button 
              className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-lg border border-cyan-500/30 transition-all hover:shadow-[0_0_10px_rgba(6,182,212,0.2)]"
              onClick={() => alert("ATOM Interface: Voice/Text Link Establishing... (Feature coming in next update)")}
            >
              <User size={14} />
              <span className="text-xs font-bold tracking-wide">TALK TO ATOM</span>
            </button>
        </div>

        <div className="command-center__content" style={{ flex: 1, overflowY: 'auto', paddingBottom: '4rem', paddingRight: '1rem' }}>
          {section.render()}
        </div>
      </section>
      
      {/* Advisor Popup */}
      <NextStepAdvisor status={status} metrics={metrics} />
      
      <RealTimeLogViewer />
    </>
  );
};
