import { Component, OnInit } from '@angular/core';
import { HttpService } from "../../app/http.service";
import { SocketService } from 'src/app/socket.service';

@Component({
    styleUrls:['./profiles.css'],
    templateUrl: 'profiles.component.html'
})
export class ProfilesComponent implements OnInit {
    records: any;
    no_prof = false;
    type = '';
    show_profiles_breadcrumb = true;
    breadcrumb_title = '';
    socketService : SocketService;    
    httpService: HttpService;
    constructor(private httpServ: HttpService, private ss: SocketService) {        
        this.records = [];
        this.socketService = this.ss;
        this.httpService = httpServ;
        this.get_list();
    }

    get_list(){
        var obj_this = this;
        let current_path = this.socketService.current_path.replace('/profiles', '');

        if (current_path.length > 0)
        {
            obj_this.breadcrumb_title = current_path.replace('/', '');
            obj_this.show_profiles_breadcrumb = false;
        }
        else
        {
            obj_this.show_profiles_breadcrumb = true;
        }
        var url = window.location.href.split("/")
        var path = url[url.length-1]
        obj_this.type = "";
        if (path == "directors"){
            obj_this.type = "director"
        }
        if (path == "admins"){
            obj_this.type = "admin"
        }
        if (path == "staff"){
            obj_this.type = "staff"
        }
        const input_data = {
            type:obj_this.type
        }
        let args = {
            app: 'meetings',
            model: 'Profile',
            method: 'get_records'
        }			
        let final_input_data = {
            params: input_data,
            args: args
        };
        obj_this.httpService.get(final_input_data,
            (result) => {
                    obj_this.records = result.records;
                    obj_this.records && obj_this.records.length > 0 ? obj_this.no_prof = false : obj_this.no_prof = true;                    
        }, null);
    }

    ngOnInit() {
        window['json_functions'].find_activate_link('.MeetingBtnWrapper');
    }
}
