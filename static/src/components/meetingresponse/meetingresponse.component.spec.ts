import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { MeetingresponseComponent } from './meetingresponse.component';
import { HttpService } from 'src/app/http.service';

describe('MeetingresponseComponent', () => {
    let component: MeetingresponseComponent;
    let fixture: ComponentFixture<MeetingresponseComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ MeetingresponseComponent ],
            providers: [HttpService], 
        })
        .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(MeetingresponseComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
