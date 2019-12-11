import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MovetomyfolderComponent } from './movetomyfolder.component';

describe('MovetomyfolderComponent', () => {
  let component: MovetomyfolderComponent;
  let fixture: ComponentFixture<MovetomyfolderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MovetomyfolderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MovetomyfolderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
