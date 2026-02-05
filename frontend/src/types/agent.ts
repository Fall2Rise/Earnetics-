export interface Agent {
  id: string;
  name: string;
  division: string;
  role: string;
  status: 'active' | 'idle' | 'busy';
  memoryEntries: number;
  specialties: string[];
}
