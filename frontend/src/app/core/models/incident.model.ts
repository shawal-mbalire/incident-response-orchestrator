export interface Alert {
  id: string;
  service: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  timestamp: string;
  metrics: Record<string, unknown>;
}

export interface Incident {
  id: string;
  alert_id: string;
  service: string;
  title: string;
  status: 'investigating' | 'identified' | 'monitoring' | 'resolved';
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  root_cause: string;
  confidence: string;
}

export interface Report {
  incident_id: string;
  executive_summary: string;
  timeline: Array<{ time: string; event: string }>;
  root_cause: string;
  confidence: 'high' | 'medium' | 'low';
  impact_assessment: string;
  recommended_actions: string[];
  supporting_evidence: Record<string, unknown>;
  generated_at: string;
}
