import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom, retry, catchError, throwError } from 'rxjs';
import { Alert, Incident, Report, ApiError, isApiError } from '../models/incident.model';

export interface LogEntry {
  timestamp: string;
  service: string;
  severity: string;
  message: string;
  labels: Record<string, string>;
}

@Injectable({ providedIn: 'root' })
export class IncidentService {
  private http = inject(HttpClient);
  private apiUrl = 'https://incident-response-backend-nkpzqdusca-uc.a.run.app/api';
  private correlationId = this.generateCorrelationId();

  private generateCorrelationId(): string {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID().substring(0, 12);
    }
    return Math.random().toString(36).substring(2, 14);
  }

  private getHeaders(): Record<string, string> {
    return { 'X-Correlation-ID': this.correlationId };
  }

  private handleError(error: HttpErrorResponse): never {
    if (error.error && isApiError(error.error)) {
      throw error.error;
    }
    throw {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred',
    } as ApiError;
  }

  async createAlert(alert: Partial<Alert>): Promise<Report> {
    return firstValueFrom(
      this.http.post<Report>(`${this.apiUrl}/alerts`, alert, {
        headers: this.getHeaders(),
      }).pipe(
        retry({ count: 1, delay: 1000 }),
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
  }

  async getIncidents(service?: string, minutes?: number): Promise<Incident[]> {
    const params: Record<string, string | number> = {};
    if (service) params['service'] = service;
    if (minutes) params['minutes'] = minutes;

    return firstValueFrom(
      this.http.get<Incident[]>(`${this.apiUrl}/incidents`, {
        params,
        headers: this.getHeaders(),
      }).pipe(
        retry({ count: 1, delay: 1000 }),
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
  }

  async getReport(incidentId: string): Promise<Report> {
    return firstValueFrom(
      this.http.get<Report>(`${this.apiUrl}/incidents/${incidentId}/report`, {
        headers: this.getHeaders(),
      }).pipe(
        retry({ count: 1, delay: 1000 }),
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
  }

  async getServices(): Promise<string[]> {
    const response = await firstValueFrom(
      this.http.get<{ services: string[] }>(`${this.apiUrl}/services`, {
        headers: this.getHeaders(),
      }).pipe(
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
    return response.services;
  }

  async getLogs(service?: string, minutes?: number): Promise<LogEntry[]> {
    const params: Record<string, string | number> = {};
    if (service) params['service'] = service;
    if (minutes) params['minutes'] = minutes;

    const response = await firstValueFrom(
      this.http.get<{ logs: LogEntry[]; count: number }>(`${this.apiUrl}/logs`, {
        params,
        headers: this.getHeaders(),
      }).pipe(
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
    return response.logs;
  }

  async analyze(service?: string, minutes?: number): Promise<{ analyzed: number; incidents_found: number; reports: Report[] }> {
    const params: Record<string, string | number> = {};
    if (service) params['service'] = service;
    if (minutes) params['minutes'] = minutes;

    return firstValueFrom(
      this.http.post<{ analyzed: number; incidents_found: number; reports: Report[] }>(
        `${this.apiUrl}/analyze`,
        {},
        { params, headers: this.getHeaders() }
      ).pipe(
        catchError((err) => {
          this.handleError(err);
          return throwError(() => err);
        }),
      )
    );
  }
}
