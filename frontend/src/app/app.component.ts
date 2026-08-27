import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-container">
      <nav class="sidebar">
        <div class="logo">
          <h1>Incident Response</h1>
          <span class="subtitle">Orchestrator</span>
        </div>
        <ul class="nav-links">
          <li>
            <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">
              Dashboard
            </a>
          </li>
          <li>
            <a routerLink="/alert" routerLinkActive="active">
              New Alert
            </a>
          </li>
        </ul>
      </nav>
      <main class="content">
        <router-outlet />
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      min-height: 100vh;
      font-family: 'Inter', sans-serif;
    }

    .sidebar {
      width: 240px;
      background: #1a1a2e;
      color: white;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
    }

    .logo h1 {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0;
    }

    .logo .subtitle {
      font-size: 0.75rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .nav-links {
      list-style: none;
      padding: 0;
      margin: 2rem 0 0;
    }

    .nav-links a {
      display: block;
      padding: 0.75rem 1rem;
      color: #ccc;
      text-decoration: none;
      border-radius: 6px;
      transition: all 0.2s;
    }

    .nav-links a:hover {
      background: rgba(255, 255, 255, 0.1);
      color: white;
    }

    .nav-links a.active {
      background: #3b82f6;
      color: white;
    }

    .content {
      flex: 1;
      background: #f5f5f5;
      padding: 2rem;
    }
  `],
})
export class AppComponent {}
