import React, { useState } from 'react';
import { AssistantConsole } from './components/assistant/AssistantConsole';
import { CommandCenter } from './components/layout/CommandCenter';
import { Header } from './components/layout/Header';
import { DashboardSection } from './types/navigation';

function App() {
  const [activeSection, setActiveSection] = useState<DashboardSection>('dashboard');

  return (
    <div className="app-container">
      <div className="aurora-overlay" />
      <Header activeSection={activeSection} onSectionChange={setActiveSection} />
      <main className="dashboard-wrapper">
        <CommandCenter activeSection={activeSection} />
      </main>
      <AssistantConsole />
    </div>
  );
}

export default App;


