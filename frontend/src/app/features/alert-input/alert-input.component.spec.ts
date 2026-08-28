import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { AlertInputComponent } from './alert-input.component';

describe('AlertInputComponent', () => {
  let component: AlertInputComponent;
  let fixture: ComponentFixture<AlertInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlertInputComponent],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(AlertInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have default severity of high', () => {
    expect(component.severity()).toBe('high');
  });

  it('should not be valid when service is empty', () => {
    expect(component.isValid()).toBeFalse();
  });

  it('should not be valid when message is too short', () => {
    component.service.set('api-gateway');
    component.message.set('short');
    expect(component.isValid()).toBeFalse();
  });

  it('should be valid when service and message are provided', () => {
    component.service.set('api-gateway');
    component.message.set('This is a test alert message');
    expect(component.isValid()).toBeTrue();
  });

  it('should render the form', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('form')).toBeTruthy();
    expect(compiled.querySelector('select#service')).toBeTruthy();
    expect(compiled.querySelector('select#severity')).toBeTruthy();
    expect(compiled.querySelector('textarea#message')).toBeTruthy();
  });
});
