import { Component, signal } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { Incident } from '../../core/models/incident.model';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  template: `
    <div class="dashboard">
      <header class="dashboard-header">
        <h1>Dashboard</h1>
        <a routerLink="/alert" class="btn-primary">New Alert</a>
      </header>

      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-value">{{ criticalCount() }}</span>
          <span class="metric-label">Critical</span>
        </div>
        <div class="metric-card">
          <span class="metric-value">{{ highCount() }}</span>
          <span class="metric-label">High</span>
        </div>
        <div class="metric-card">
          <span class="metric-value">{{ totalIncidents() }}</span>
          <span class="metric-label">Total Incidents</span>
        </div>
      </div>

      <div class="incidents-section">
        <h2>Recent Incidents</h2>
        @if (incidents.isLoading()) {
          <div class="loading">Loading incidents...</div>
        } @else if (incidents.value().length === 0) {
          <div class="empty-state">
            <p>No incidents found</p>
            <a routerLink="/alert" class="btn-secondary">Create First Alert</a>
          </div>
        } @else {
          <div class="incidents-list">
            @for (incident of incidents.value(); track incident.id) {
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
  `,
  styles: [`
    .dashboard {
      max-width: 1200px;
      margin: 0 auto;
    }

    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .dashboard-header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 500;
      transition: background 0.2s;
    }

    .btn-primary:hover {
      background: #2563eb;
    }

    .btn-secondary {
      background: #e5e7eb;
      color: #374151;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 500;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .metric-card {
      background: white;
      border-radius: 8px;
      padding: 1.5rem;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .metric-value {
      display: block;
      font-size: 2rem;
      font-weight: 700;
      color: #1a1a2e;
    }

    .metric-label {
      font-size: 0.875rem;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .incidents-section h2 {
      font-size: 1.125rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0 0 1rem;
    }

    .incidents-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .incident-card {
      background: white;
      border-radius: 8px;
      padding: 1rem 1.25rem;
      text-decoration: none;
      color: inherit;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      transition: box-shadow 0.2s;
    }

    .incident-card:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .incident-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .service-name {
      font-size: 0.75rem;
      font-weight: 600;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .status-badge {
      font-size: 0.75rem;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-weight: 500;
    }

    .status-badge.investigating { background: #fef3c7; color: #92400e; }
    .status-badge.identified { background: #dbeafe; color: #1e40af; }
    .status-badge.monitoring { background: #d1fae5; color: #065f46; }
    .status-badge.resolved { background: #e5e7eb; color: #374151; }

    .incident-card h3 {
      font-size: 1rem;
      font-weight: 500;
      margin: 0 0 0.5rem;
      color: #1a1a2e;
    }

    .incident-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.75rem;
      color: #6b7280;
    }

    .confidence.high { color: #059669; }
    .confidence.medium { color: #d97706; }
    .confidence.low { color: #dc2626; }

    .loading, .empty-state {
      text-align: center;
      padding: 3rem;
      background: white;
      border-radius: 8px;
      color: #6b7280;
    }

    .empty-state p {
      margin: 0 0 1rem;
    }
  `],
})
export class DashboardComponent {
  selectedService = signal('');
  timeRange = signal(30);

  incidents = httpResource<Incident[]>(
    () => ({
      url: '/api/incidents',
      params: {
        service: this.selectedService(),
        minutes: this.timeRange(),
      },
    }),
    { defaultValue: [] }
  );

  criticalCount = () =>
    this.incidents.value().filter((i) => i.confidence === 'high').length;

  highCount = () =>
    this.incidents.value().filter((i) => i.confidence === 'medium').length;

  totalIncidents = () => this.incidents.value().length;

  formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }
}
