import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then(
        (m) => m.DashboardComponent
      ),
  },
  {
    path: 'alert',
    loadComponent: () =>
      import('./features/alert-input/alert-input.component').then(
        (m) => m.AlertInputComponent
      ),
  },
  {
    path: 'incidents/:id',
    loadComponent: () =>
      import('./features/incident-report/incident-report.component').then(
        (m) => m.IncidentReportComponent
      ),
  },
  { path: '**', redirectTo: '' },
];
