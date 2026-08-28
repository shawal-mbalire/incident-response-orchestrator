import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have zero total incidents initially', () => {
    expect(component.totalIncidents()).toBe(0);
  });

  it('should render dashboard header', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.dashboard-header h1')?.textContent).toContain('Dashboard');
  });

  it('should render metrics grid', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const metricCards = compiled.querySelectorAll('.metric-card');
    expect(metricCards.length).toBe(3);
  });

  it('should render incidents section', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.incidents-section h2')?.textContent).toContain('Recent Incidents');
  });

  it('should format dates correctly', () => {
    const date = '2024-01-15T10:30:00Z';
    const formatted = component.formatDate(date);
    expect(formatted).toBeTruthy();
    expect(typeof formatted).toBe('string');
  });
});
