import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewmembersComponent } from './viewmembers.component';

describe('ViewmembersComponent', () => {
  let component: ViewmembersComponent;
  let fixture: ComponentFixture<ViewmembersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ViewmembersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewmembersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
