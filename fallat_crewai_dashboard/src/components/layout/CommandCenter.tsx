import React from 'react';
import { AgentsPanel } from '../dashboard/AgentsPanel';
import { IntelligencePanel } from '../dashboard/IntelligencePanel';
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

interface CommandCenterProps {
  activeSection: DashboardSection;
}

const renderDashboard = () => (
  <div className="command-grid">
    <div className="command-panel command-panel--visual">
      <Office3DView />
    </div>
    <div className="command-panel command-panel--metrics">
      <PerformanceMetrics />
      <OperationsPulse compact />
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
      <ModelManager />
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
      <IntelligencePanel />
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
    case 'dashboard':
    default:
      content = renderDashboard();
      break;
  }

  return <section className="command-center">{content}</section>;
};
