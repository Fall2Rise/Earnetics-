export interface Contact {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  type?: string;
  source?: string;
  tags?: string;
  notes?: string;
}

export interface Deal {
  id: number;
  contact_id?: number;
  title: string;
  pipeline: string;
  stage: string;
  value_estimate?: number;
  priority?: string;
}

export interface Task {
  id: number;
  title: string;
  status: string;
  owner?: string;
  due_at?: string;
}
