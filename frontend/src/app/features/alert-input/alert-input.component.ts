import { Component, signal, inject } from '@angular/core';
import { Router } from '@angular/router';
import { IncidentService } from '../../core/services/incident.service';

@Component({
  selector: 'app-alert-input',
  template: `
    <div class="alert-form-container">
      <h1>Create Alert</h1>
      <p class="description">Trigger an incident analysis for a service.</p>

      <form (submit)="onSubmit($event)" class="alert-form">
        <div class="form-group">
          <label for="service">Service Name</label>
          <select id="service" [value]="service()" (change)="onServiceChange($event)">
            <option value="">Select a service</option>
            <option value="api-gateway">API Gateway</option>
            <option value="user-service">User Service</option>
            <option value="payment-service">Payment Service</option>
            <option value="notification-service">Notification Service</option>
          </select>
        </div>

        <div class="form-group">
          <label for="severity">Severity</label>
          <select id="severity" [value]="severity()" (change)="onSeverityChange($event)">
            <option value="critical">Critical</option>
            <option value="high" selected>High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div class="form-group">
          <label for="message">Alert Message</label>
          <textarea
            id="message"
            rows="3"
            [value]="message()"
            (input)="onMessageChange($event)"
            placeholder="Describe the alert condition..."
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-cancel" (click)="goBack()">Cancel</button>
          <button
            type="submit"
            class="btn-submit"
            [disabled]="isSubmitting() || !isValid()"
          >
            @if (isSubmitting()) {
              Analyzing...
            } @else {
              Trigger Analysis
            }
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .alert-form-container {
      max-width: 600px;
      margin: 0 auto;
    }

    h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0 0 0.5rem;
    }

    .description {
      color: #6b7280;
      margin: 0 0 1.5rem;
    }

    .alert-form {
      background: white;
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .form-group {
      margin-bottom: 1.25rem;
    }

    label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.5rem;
    }

    select, textarea {
      width: 100%;
      padding: 0.625rem 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 0.875rem;
      font-family: inherit;
      transition: border-color 0.2s;
    }

    select:focus, textarea:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    textarea {
      resize: vertical;
    }

    .form-actions {
      display: flex;
      gap: 0.75rem;
      justify-content: flex-end;
      margin-top: 1.5rem;
    }

    .btn-cancel {
      background: #e5e7eb;
      color: #374151;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      border: none;
      font-weight: 500;
      cursor: pointer;
    }

    .btn-submit {
      background: #3b82f6;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      border: none;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }

    .btn-submit:hover:not(:disabled) {
      background: #2563eb;
    }

    .btn-submit:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `],
})
export class AlertInputComponent {
  private incidentService = inject(IncidentService);
  private router = inject(Router);

  service = signal('');
  severity = signal('high');
  message = signal('');
  isSubmitting = signal(false);

  onServiceChange(event: Event) {
    this.service.set((event.target as HTMLSelectElement).value);
  }

  onSeverityChange(event: Event) {
    this.severity.set((event.target as HTMLSelectElement).value);
  }

  onMessageChange(event: Event) {
    this.message.set((event.target as HTMLTextAreaElement).value);
  }

  isValid(): boolean {
    return this.service().length > 0 && this.message().length >= 10;
  }

  async onSubmit(event: Event) {
    event.preventDefault();
    if (!this.isValid() || this.isSubmitting()) return;

    this.isSubmitting.set(true);
    try {
      const report = await this.incidentService.createAlert({
        service: this.service(),
        severity: this.severity() as 'critical' | 'high' | 'medium' | 'low',
        message: this.message(),
      });
      this.router.navigate(['/incidents', report.incident_id]);
    } catch (error) {
      console.error('Failed to create alert:', error);
    } finally {
      this.isSubmitting.set(false);
    }
  }

  goBack() {
    this.router.navigate(['/']);
  }
}
