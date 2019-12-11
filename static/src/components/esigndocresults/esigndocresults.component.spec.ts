import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EsigndocresultsComponent } from './esigndocresults.component';

describe('EsigndocresultsComponent', () => {
  let component: EsigndocresultsComponent;
  let fixture: ComponentFixture<EsigndocresultsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EsigndocresultsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EsigndocresultsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
