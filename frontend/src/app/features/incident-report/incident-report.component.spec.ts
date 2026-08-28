import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { IncidentReportComponent } from './incident-report.component';

describe('IncidentReportComponent', () => {
  let component: IncidentReportComponent;
  let fixture: ComponentFixture<IncidentReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IncidentReportComponent],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(IncidentReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render back link', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const backLink = compiled.querySelector('.back-link');
    expect(backLink).toBeTruthy();
    expect(backLink?.textContent?.trim()).toContain('Back to Dashboard');
  });

  it('should format time correctly', () => {
    const time = '2024-01-15T10:30:00Z';
    const formatted = component.formatTime(time);
    expect(formatted).toBeTruthy();
    expect(typeof formatted).toBe('string');
  });

  it('should format JSON correctly', () => {
    const obj = { key: 'value', nested: { a: 1 } };
    const formatted = component.formatJson(obj);
    expect(formatted).toContain('"key": "value"');
    expect(formatted).toContain('"nested"');
  });
});
