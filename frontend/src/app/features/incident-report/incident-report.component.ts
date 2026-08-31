import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { httpResource } from '@angular/common/http';
import { UpperCasePipe } from '@angular/common';
import { Report, isApiError } from '../../core/models/incident.model';

@Component({
  selector: 'app-incident-report',
  imports: [RouterLink, UpperCasePipe],
  template: `
    <div class="report-container">
      <a routerLink="/" class="back-link">&larr; Back to Dashboard</a>

      @if (report.isLoading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Analyzing incident...</p>
        </div>
      } @else if (report.error()) {
        <div class="error">
          <p>{{ getErrorMessage(report.error()) }}</p>
          <button (click)="report.reload()">Retry</button>
        </div>
      } @else if (report.value(); as data) {
        <header class="report-header">
          <h1>Incident Report</h1>
          <span class="incident-id">{{ data.incident_id }}</span>
        </header>

        @if (data.correlation_id) {
          <div class="correlation-id">
            Correlation ID: {{ data.correlation_id }}
          </div>
        }

        <div class="report-section summary">
          <h2>Executive Summary</h2>
          <p>{{ data.executive_summary }}</p>
        </div>

        <div class="report-section confidence">
          <h2>Root Cause Confidence</h2>
          <span class="confidence-badge" [class]="data.confidence">
            {{ data.confidence | uppercase }}
          </span>
        </div>

        <div class="report-section root-cause">
          <h2>Root Cause Analysis</h2>
          <p>{{ data.root_cause }}</p>
        </div>

        <div class="report-section timeline">
          <h2>Timeline</h2>
          <div class="timeline-list">
            @for (entry of data.timeline; track entry.time) {
              <div class="timeline-entry">
                <span class="time">{{ formatTime(entry.time) }}</span>
                <span class="event">{{ entry.event }}</span>
              </div>
            }
          </div>
        </div>

        <div class="report-section impact">
          <h2>Impact Assessment</h2>
          <p>{{ data.impact_assessment }}</p>
        </div>

        <div class="report-section actions">
          <h2>Recommended Actions</h2>
          <ul>
            @for (action of data.recommended_actions; track action) {
              <li>{{ action }}</li>
            }
          </ul>
        </div>

        <div class="report-section evidence">
          <h2>Supporting Evidence</h2>
          <div class="evidence-grid">
            @if (data.supporting_evidence['metrics']; as metrics) {
              <div class="evidence-card">
                <h3>Metrics</h3>
                <pre>{{ formatJson(metrics) }}</pre>
              </div>
            }
            @if (data.supporting_evidence['deployments']; as deploys) {
              <div class="evidence-card">
                <h3>Recent Deployments</h3>
                <pre>{{ formatJson(deploys) }}</pre>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .report-container {
      max-width: 900px;
      margin: 0 auto;
    }

    .back-link {
      display: inline-block;
      color: #3b82f6;
      text-decoration: none;
      font-size: 0.875rem;
      margin-bottom: 1.5rem;
    }

    .back-link:hover {
      text-decoration: underline;
    }

    .report-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .report-header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
    }

    .incident-id {
      font-family: monospace;
      font-size: 0.75rem;
      color: #6b7280;
      background: #f3f4f6;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
    }

    .correlation-id {
      font-family: monospace;
      font-size: 0.75rem;
      color: #6b7280;
      background: #f3f4f6;
      padding: 0.5rem 0.75rem;
      border-radius: 4px;
      margin-bottom: 1rem;
    }

    .report-section {
      background: white;
      border-radius: 8px;
      padding: 1.25rem;
      margin-bottom: 1rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .report-section h2 {
      font-size: 0.875rem;
      font-weight: 600;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 0 0 0.75rem;
    }

    .report-section p {
      margin: 0;
      line-height: 1.6;
      color: #374151;
    }

    .confidence-badge {
      display: inline-block;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.875rem;
    }

    .confidence-badge.high { background: #d1fae5; color: #065f46; }
    .confidence-badge.medium { background: #fef3c7; color: #92400e; }
    .confidence-badge.low { background: #fee2e2; color: #991b1b; }

    .timeline-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .timeline-entry {
      display: flex;
      gap: 1rem;
      padding: 0.5rem;
      background: #f9fafb;
      border-radius: 4px;
    }

    .timeline-entry .time {
      font-family: monospace;
      font-size: 0.75rem;
      color: #6b7280;
      min-width: 180px;
    }

    .timeline-entry .event {
      font-size: 0.875rem;
      color: #374151;
    }

    .report-section ul {
      margin: 0;
      padding-left: 1.25rem;
    }

    .report-section li {
      margin-bottom: 0.5rem;
      color: #374151;
      line-height: 1.5;
    }

    .evidence-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }

    .evidence-card {
      background: #f9fafb;
      border-radius: 6px;
      padding: 1rem;
    }

    .evidence-card h3 {
      font-size: 0.75rem;
      font-weight: 600;
      color: #6b7280;
      margin: 0 0 0.5rem;
    }

    .evidence-card pre {
      font-size: 0.75rem;
      overflow-x: auto;
      margin: 0;
      color: #374151;
    }

    .loading {
      text-align: center;
      padding: 4rem;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #e5e7eb;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error {
      text-align: center;
      padding: 3rem;
      background: white;
      border-radius: 8px;
      color: #dc2626;
    }

    .error button {
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
  `],
})
export class IncidentReportComponent {
  private route = inject(ActivatedRoute);

  report = httpResource<Report>(() => {
    const id = this.route.snapshot.paramMap.get('id');
    return {
      url: `/api/incidents/${id}/report`,
    };
  });

  getErrorMessage(err: unknown): string {
    if (isApiError(err)) {
      return err.message;
    }
    return 'Failed to load report. Please try again.';
  }

  formatTime(iso: string): string {
    return new Date(iso).toLocaleTimeString();
  }

  formatJson(obj: unknown): string {
    return JSON.stringify(obj, null, 2);
  }
}
