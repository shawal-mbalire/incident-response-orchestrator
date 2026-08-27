import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Alert, Incident, Report } from '../models/incident.model';

@Injectable({ providedIn: 'root' })
export class IncidentService {
  private http = inject(HttpClient);
  private apiUrl = '/api';

  async createAlert(alert: Partial<Alert>): Promise<Report> {
    return firstValueFrom(
      this.http.post<Report>(`${this.apiUrl}/alerts`, alert)
    );
  }

  async getIncidents(service?: string, minutes?: number): Promise<Incident[]> {
    const params: Record<string, string | number> = {};
    if (service) params['service'] = service;
    if (minutes) params['minutes'] = minutes;

    return firstValueFrom(
      this.http.get<Incident[]>(`${this.apiUrl}/incidents`, { params })
    );
  }

  async getReport(incidentId: string): Promise<Report> {
    return firstValueFrom(
      this.http.get<Report>(`${this.apiUrl}/incidents/${incidentId}/report`)
    );
  }

  async getServices(): Promise<string[]> {
    const response = await firstValueFrom(
      this.http.get<{ services: string[] }>(`${this.apiUrl}/services`)
    );
    return response.services;
  }
}
