import React from 'react';
import { AgentsPanel } from '../dashboard/AgentsPanel';
import { IntelligencePanel } from '../dashboard/IntelligencePanel';
import { SignalDashboard } from '../dashboard/SignalDashboard';
import { TruthLibraryBrowser } from '../dashboard/TruthLibraryBrowser';
import { LeadVaultBrowser } from '../dashboard/LeadVaultBrowser';
import { ExecutiveInbox } from '../dashboard/ExecutiveInbox';
import { OpportunityBacklogKanban } from '../dashboard/OpportunityBacklogKanban';
import { ExperimentsLab } from '../dashboard/ExperimentsLab';
import { Office3DView } from '../dashboard/Office3DView';
import { OperationsPulse } from '../dashboard/OperationsPulse';
import { PerformanceMetrics } from '../dashboard/PerformanceMetrics';
import { DashboardSection } from '../../types/navigation';
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

interface CommandCenterProps {
  activeSection: DashboardSection;
}

const renderDashboard = () => (
  <div className="panel-stack">
    {/* 3D Nexus on top */}
    <div className="command-panel command-panel--visual">
      <Office3DView />
    </div>
    {/* Operating Pulse on bottom */}
    <div className="command-panel">
      <OperationsPulse />
    </div>
    {/* Performance Metrics */}
    <div className="command-panel">
      <PerformanceMetrics />
    </div>
    {/* Dashboard Controls */}
    <div className="command-panel">
      <DashboardControls />
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

export const CommandCenter: React.FC<CommandCenterProps> = ({ activeSection }) => {
  let content: React.ReactNode;
  switch (activeSection) {
    case 'agents':
      content = renderAgents();
      break;
    case 'workflows':
      content = renderWorkflows();
      break;
    case 'intelligence':
      content = renderIntelligence();
      break;
    case 'financial':
      content = renderFinancial();
      break;
    case 'security':
      content = renderSecurity();
      break;
    case 'leads':
      content = renderLeads();
      break;
    case 'marketing':
      content = renderMarketing();
      break;
    case 'subscribers':
      content = renderSubscribers();
      break;
    case 'head-office':
      content = renderHeadOffice();
      break;
    case 'dashboard':
    default:
      content = renderDashboard();
      break;
  }

  return (
    <>
      <section className="command-center">{content}</section>
      <RealTimeLogViewer />
    </>
  );
};
