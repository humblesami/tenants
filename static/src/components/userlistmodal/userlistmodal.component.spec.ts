import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserlistmodalComponent } from './userlistmodal.component';

describe('UserlistmodalComponent', () => {
  let component: UserlistmodalComponent;
  let fixture: ComponentFixture<UserlistmodalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UserlistmodalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserlistmodalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
