import { Component, signal, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { IncidentService, LogEntry } from '../../core/services/incident.service';
import { Incident, Report, isApiError } from '../../core/models/incident.model';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  template: `
    <div class="dashboard">
      <header class="dashboard-header">
        <h1>Incident Response Orchestrator</h1>
        <div class="header-actions">
          <button (click)="runAnalysis()" class="btn-analyze" [disabled]="analyzing()">
            {{ analyzing() ? 'Analyzing...' : 'Analyze with Gemini' }}
          </button>
        </div>
      </header>

      @if (error()) {
        <div class="error-banner">
          <span>{{ error() }}</span>
          <button (click)="error.set(null)" class="error-dismiss">&times;</button>
        </div>
      }

      @if (analysisResult()) {
        <div class="analysis-result">
          <h2>Gemini Analysis Complete</h2>
          <p>Scanned {{ analysisResult()!.analyzed }} services, found {{ analysisResult()!.incidents_found }} issues</p>
          @for (report of analysisResult()!.reports; track report.incident_id) {
            <a [routerLink]="['/incidents', report.incident_id]" class="report-card">
              <span class="confidence-badge" [class]="report.confidence">{{ report.confidence }}</span>
              <p>{{ report.executive_summary }}</p>
            </a>
          }
        </div>
      }

      <div class="filters">
        <select [value]="selectedService()" (change)="onServiceChange($event)">
          <option value="">All Services</option>
          @for (svc of services(); track svc) {
            <option [value]="svc">{{ svc }}</option>
          }
        </select>
        <select [value]="timeRange()" (change)="onTimeRangeChange($event)">
          <option [value]="15">Last 15 min</option>
          <option [value]="30">Last 30 min</option>
          <option [value]="60">Last 1 hour</option>
          <option [value]="120">Last 2 hours</option>
        </select>
        <button (click)="loadLogs()" class="btn-refresh">Refresh Logs</button>
      </div>

      <div class="content-grid">
        <div class="logs-section">
          <h2>Centralized Logs</h2>
          @if (loadingLogs()) {
            <div class="loading">Loading logs...</div>
          } @else if (logs().length === 0) {
            <div class="empty-state">No logs found</div>
          } @else {
            <div class="logs-list">
              @for (log of logs(); track log.timestamp + log.message) {
                <div class="log-entry" [class]="log.severity.toLowerCase()">
                  <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                  <span class="log-service">{{ log.service }}</span>
                  <span class="log-severity" [class]="log.severity.toLowerCase()">{{ log.severity }}</span>
                  <span class="log-message">{{ log.message }}</span>
                </div>
              }
            </div>
          }
        </div>

        <div class="incidents-section">
          <h2>Recent Incidents</h2>
          @if (loading()) {
            <div class="loading">Loading incidents...</div>
          } @else if (incidents().length === 0) {
            <div class="empty-state">
              <p>No incidents found</p>
              <p class="hint">Run "Analyze with Gemini" to detect issues</p>
            </div>
          } @else {
            <div class="incidents-list">
              @for (incident of incidents(); track incident.id) {
                <a [routerLink]="['/incidents', incident.id]" class="incident-card">
                  <div class="incident-header">
                    <span class="service-name">{{ incident.service }}</span>
                    <span class="status-badge" [class]="incident.status">
                      {{ incident.status }}
                    </span>
                  </div>
                  <h3>{{ incident.title }}</h3>
                  <div class="incident-meta">
                    <span class="time">{{ formatDate(incident.created_at) }}</span>
                    <span class="confidence" [class]="incident.confidence">
                      {{ incident.confidence }} confidence
                    </span>
                  </div>
                </a>
              }
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      max-width: 1400px;
      margin: 0 auto;
    }

    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .dashboard-header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
    }

    .header-actions {
      display: flex;
      gap: 0.75rem;
    }

    .btn-analyze {
      background: #8b5cf6;
      color: white;
      padding: 0.5rem 1.25rem;
      border: none;
      border-radius: 6px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }

    .btn-analyze:hover:not(:disabled) {
      background: #7c3aed;
    }

    .btn-analyze:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .analysis-result {
      background: #f0fdf4;
      border: 1px solid #86efac;
      border-radius: 8px;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
    }

    .analysis-result h2 {
      font-size: 1rem;
      font-weight: 600;
      color: #166534;
      margin: 0 0 0.5rem;
    }

    .analysis-result p {
      color: #15803d;
      margin: 0 0 1rem;
      font-size: 0.875rem;
    }

    .report-card {
      display: block;
      background: white;
      border-radius: 6px;
      padding: 0.75rem 1rem;
      margin-bottom: 0.5rem;
      text-decoration: none;
      color: inherit;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .confidence-badge {
      display: inline-block;
      font-size: 0.75rem;
      padding: 0.125rem 0.5rem;
      border-radius: 4px;
      font-weight: 500;
      margin-right: 0.5rem;
    }

    .confidence-badge.high { background: #d1fae5; color: #065f46; }
    .confidence-badge.medium { background: #fef3c7; color: #92400e; }
    .confidence-badge.low { background: #fee2e2; color: #991b1b; }

    .error-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fee2e2;
      color: #991b1b;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      margin-bottom: 1rem;
      font-size: 0.875rem;
    }

    .error-dismiss {
      background: none;
      border: none;
      color: #991b1b;
      font-size: 1.25rem;
      cursor: pointer;
      padding: 0 0.25rem;
    }

    .filters {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }

    .filters select, .btn-refresh {
      padding: 0.5rem 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 0.875rem;
      background: white;
    }

    .btn-refresh {
      background: #3b82f6;
      color: white;
      border-color: #3b82f6;
      cursor: pointer;
    }

    .content-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }

    .logs-section, .incidents-section {
      background: white;
      border-radius: 8px;
      padding: 1.25rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .logs-section h2, .incidents-section h2 {
      font-size: 1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0 0 1rem;
    }

    .logs-list {
      max-height: 500px;
      overflow-y: auto;
      font-family: monospace;
      font-size: 0.75rem;
    }

    .log-entry {
      display: grid;
      grid-template-columns: 140px 120px 60px 1fr;
      gap: 0.5rem;
      padding: 0.375rem 0.5rem;
      border-bottom: 1px solid #f3f4f6;
      align-items: start;
    }

    .log-entry.error { background: #fef2f2; }
    .log-entry.critical { background: #fef2f2; }
    .log-entry.warning { background: #fffbeb; }

    .log-time { color: #6b7280; }
    .log-service { color: #3b82f6; font-weight: 500; }
    .log-severity { font-weight: 600; }
    .log-severity.error, .log-severity.critical { color: #dc2626; }
    .log-severity.warning { color: #d97706; }
    .log-severity.info { color: #3b82f6; }
    .log-message { color: #374151; word-break: break-word; }

    .incidents-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .incident-card {
      display: block;
      background: #f9fafb;
      border-radius: 6px;
      padding: 0.75rem 1rem;
      text-decoration: none;
      color: inherit;
      transition: box-shadow 0.2s;
    }

    .incident-card:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .incident-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.25rem;
    }

    .service-name {
      font-size: 0.75rem;
      font-weight: 600;
      color: #6b7280;
      text-transform: uppercase;
    }

    .status-badge {
      font-size: 0.625rem;
      padding: 0.125rem 0.375rem;
      border-radius: 4px;
    }

    .status-badge.investigating { background: #fef3c7; color: #92400e; }
    .status-badge.identified { background: #dbeafe; color: #1e40af; }
    .status-badge.monitoring { background: #d1fae5; color: #065f46; }
    .status-badge.resolved { background: #e5e7eb; color: #374151; }

    .incident-card h3 {
      font-size: 0.875rem;
      font-weight: 500;
      margin: 0 0 0.25rem;
      color: #1a1a2e;
    }

    .incident-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.625rem;
      color: #6b7280;
    }

    .confidence.high { color: #059669; }
    .confidence.medium { color: #d97706; }
    .confidence.low { color: #dc2626; }

    .loading, .empty-state {
      text-align: center;
      padding: 2rem;
      color: #6b7280;
      font-size: 0.875rem;
    }

    .hint {
      font-size: 0.75rem;
      color: #9ca3af;
    }
  `],
})
export class DashboardComponent implements OnInit {
  private incidentService = inject(IncidentService);

  selectedService = signal('');
  timeRange = signal(30);
  incidents = signal<Incident[]>([]);
  services = signal<string[]>([]);
  logs = signal<LogEntry[]>([]);
  loading = signal(false);
  loadingLogs = signal(false);
  analyzing = signal(false);
  error = signal<string | null>(null);
  analysisResult = signal<{ analyzed: number; incidents_found: number; reports: Report[] } | null>(null);

  async ngOnInit() {
    await Promise.all([this.loadIncidents(), this.loadServices(), this.loadLogs()]);
  }

  async loadIncidents() {
    this.loading.set(true);
    this.error.set(null);
    try {
      const data = await this.incidentService.getIncidents(
        this.selectedService() || undefined,
        this.timeRange(),
      );
      this.incidents.set(data);
    } catch (err) {
      const message = isApiError(err) ? err.message : 'Failed to load incidents';
      this.error.set(message);
      this.incidents.set([]);
    } finally {
      this.loading.set(false);
    }
  }

  async loadLogs() {
    this.loadingLogs.set(true);
    try {
      const data = await this.incidentService.getLogs(
        this.selectedService() || undefined,
        this.timeRange(),
      );
      this.logs.set(data);
    } catch {
      this.logs.set([]);
    } finally {
      this.loadingLogs.set(false);
    }
  }

  async loadServices() {
    try {
      const data = await this.incidentService.getServices();
      this.services.set(data);
    } catch {
      this.services.set(['incident-response-backend', 'incident-response-frontend']);
    }
  }

  async runAnalysis() {
    this.analyzing.set(true);
    this.error.set(null);
    try {
      const result = await this.incidentService.analyze(
        this.selectedService() || undefined,
        this.timeRange(),
      );
      this.analysisResult.set(result);
      await this.loadIncidents();
    } catch (err) {
      const message = isApiError(err) ? err.message : 'Analysis failed';
      this.error.set(message);
    } finally {
      this.analyzing.set(false);
    }
  }

  onServiceChange(event: Event) {
    this.selectedService.set((event.target as HTMLSelectElement).value);
    this.loadIncidents();
    this.loadLogs();
  }

  onTimeRangeChange(event: Event) {
    this.timeRange.set(Number((event.target as HTMLSelectElement).value));
    this.loadIncidents();
    this.loadLogs();
  }

  formatTime(iso: string): string {
    return new Date(iso).toLocaleTimeString();
  }

  formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }
}
