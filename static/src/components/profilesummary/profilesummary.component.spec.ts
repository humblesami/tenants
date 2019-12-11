import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfilesummaryComponent } from './profilesummary.component';

describe('ProfilesummaryComponent', () => {
  let component: ProfilesummaryComponent;
  let fixture: ComponentFixture<ProfilesummaryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProfilesummaryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProfilesummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
