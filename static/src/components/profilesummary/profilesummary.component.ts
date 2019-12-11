import { Component, OnInit, Input } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
    selector: 'app-profilesummary',
    templateUrl: './profilesummary.component.html',
    styleUrls: ['./profilesummary.component.css',
        '../profiledetails/profiledetails.css',
        '../roster/roster.component.css'
    ]
})
export class ProfilesummaryComponent implements OnInit {
    @Input() user_id: number;
    profile_data;
    server_url = window['server_url'];
    constructor(private httpService: HttpService, public activeModal: NgbActiveModal) {}
    ngOnInit() {
        const obj_this = this;
        let input_data = {
            user_id: this.user_id
        };
        console.log(input_data, 8);
        let args = {
            app: 'meetings',
            model: 'Profile',
            method: 'get_profile_summary'
        }
        let final_input_data = {
            params: input_data,
            args: args
        }
        obj_this.httpService.get(final_input_data, (data) => {
            obj_this.profile_data = data;
        }, null);
    }
}