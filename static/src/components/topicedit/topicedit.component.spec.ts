import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TopiceditComponent } from './topicedit.component';

describe('TopiceditComponent', () => {
  let component: TopiceditComponent;
  let fixture: ComponentFixture<TopiceditComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TopiceditComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TopiceditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
