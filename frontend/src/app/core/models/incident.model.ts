export interface ApiError {
  code: string;
  message: string;
  field?: string;
}

export interface Alert {
  id: string;
  service: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  timestamp: string;
  metrics: Record<string, unknown>;
  correlation_id?: string;
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
  confidence: 'high' | 'medium' | 'low';
  correlation_id?: string;
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
  correlation_id?: string;
}

export function isApiError(obj: unknown): obj is ApiError {
  return typeof obj === 'object' && obj !== null && 'code' in obj && 'message' in obj;
}

export function validateAlert(alert: Partial<Alert>): string[] {
  const errors: string[] = [];
  if (!alert.service?.trim()) errors.push('Service is required');
  if (!alert.message?.trim()) errors.push('Message is required');
  if (alert.message && alert.message.length < 10) errors.push('Message must be at least 10 characters');
  return errors;
}
