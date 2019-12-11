import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../app/http.service'
import { Router, ActivatedRoute, Params } from '@angular/router';
declare var $: any;

@Component({
    styleUrls:['./meetings.css'],
    templateUrl: 'meetings.component.html'
})
export class MeetingsComponent implements OnInit {
    no_meet = false;
    meeting_list = [];
    active_meeting: any;
    show = false;
    meeting_type: string;
    heading = 'Home';
    bread_crumb = {
		items: [],
		title: ''
	};
    offset: number;
    limit: number;
    total_records : number;
    httpService: HttpService;
    constructor(private httpServ: HttpService, public router: Router, private route: ActivatedRoute) {
        this.offset = 0;
        this.limit = 2;
        this.httpService = httpServ;
        this.total_records = 0;
    }

    ngOnInit() {
        window['json_functions'].find_activate_link('.MeetingBtnWrapper');
        this.get_list();
    }

    count: number;
    get_list(){
        var url_segments = this.route.snapshot.url;
        this.meeting_type = url_segments[url_segments.length -1].path;
        let obj_this = this;
        var success_cb = function (result) {
            for(var i in result.records)
            {
                var start = result.records[i]['start'];
                start = window['dt_functions'].meeting_time(start);
                result.records[i]['start_dt'] = start;
            }
            obj_this.total_records = result.total;
            obj_this.count = result.records.length;
            obj_this.meeting_list = result.records || [];
            // console.log(obj_this.total_records,obj_this.meeting_list.length,  1411);
            obj_this.meeting_list.length > 0 ? obj_this.no_meet = false : obj_this.no_meet = true;
        };

        let input_data = {
            meeting_type: obj_this.meeting_type
        };

        var failure_cb = function (error) {
        };
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'get_records'
        }
        let final_input_data = {
            params: input_data,
            args: args
        };
        this.httpService.get(final_input_data, success_cb, failure_cb);
    }
}
