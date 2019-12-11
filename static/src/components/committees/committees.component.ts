import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { HttpService } from '../../app/http.service'
import { SocketService } from 'src/app/socket.service';

@Component({
    styleUrls:['./committees.css'],
    templateUrl: 'committees.component.html'    
})
export class CommitteesComponent implements OnInit {
    records = [];
    no_committees = false;
    heading = 'Committees';
    bread_crumb = {
		items: [],
		title: ''
    };
    socketService: SocketService
    img: string = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/220px-User_icon_2.svg.png';

    httpService: HttpService;
    constructor(private httpServ: HttpService, private ss: SocketService) {
        const obj_this = this;
        this.socketService = this.ss;
        this.httpService = httpServ;
        this.get_list();
    }

    get_list()
    {
        var obj_this = this;
        var success_cb = function (result) {
            // console.log(result)
            obj_this.records = result.records;
            obj_this.records.length > 0 ? obj_this.no_committees = false : obj_this.no_committees = true;
        };
        let args = {
            app: 'meetings',
            model: 'Committee',
            method: 'get_records'
        }
        var input_data = {
            params :{paging : {offset: 0, limit: 20}},
            args: args
        };
        this.httpService.get(input_data, success_cb, null);
    }

    ngOnInit() {
    }
}
