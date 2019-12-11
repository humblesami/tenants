import { Component, OnInit, Input } from '@angular/core';
import { HttpService } from "../../app/http.service";
import { Router, ActivatedRoute, Params } from '@angular/router';
import { SocketService } from 'src/app/socket.service';

declare var $: any;

@Component({
    selector: 'app-votings',
    templateUrl: './votings.component.html',
    styleUrls: ['./votings.css', '../esigndocs/esigndocs.css']
})
export class VotingsComponent implements OnInit {
    @Input() loaded_as_child: any;
    @Input() to_do_only: any;

    loading = true;
    socketService: SocketService;
    no_meet = false;
    records = [];
    active_meeting: any;
    show = false;
    meeting_type: string;
    heading = 'Home';
    bread_crumb = {
    items: [],
    title: ''
};
httpService: HttpService;
constructor(private httpServ: HttpService, 
    public router: Router, private route: ActivatedRoute,
    private sock: SocketService) {
    this.httpService = httpServ;
    this.socketService = sock;
}

get_records(el, state)
{
    let obj_this = this;
    if(!obj_this.to_do_only)
        localStorage.setItem(obj_this.state_name, state);
    $(el).parent().find('.active').removeClass('active');
    $(el).addClass('active');
    obj_this.get_list(state);
}

prev_state = undefined;

get_list(state)
{
    let obj_this = this;
    let offset = undefined;
    let limit = undefined;
    
    if(!state)
    {
        state = localStorage.getItem(obj_this.state_name);
    }
    if(obj_this.prev_state != state)
    {
        obj_this.loading = true;
        offset = 0;
    }
    obj_this.prev_state = state;

    let input_data = { states: state, meeting_type: obj_this.meeting_type, offset: offset, limit: limit};
    var success_cb = function (result) {
        //console.log(result);
        for(var i in result.records)
        {
            var open_date = result.records[i]['open_date'];
            open_date= window['dt_functions'].meeting_time(open_date);
            result.records[i]['open_date'] = open_date;
        }
        obj_this.records = result.records;
        obj_this.records.length > 0 ? obj_this.no_meet = false : obj_this.no_meet = true;            
        obj_this.loading = false;
    };
    let args = {
        app: 'voting',
        model: 'Voting',
        method: 'get_records'
    }			
    let final_input_data = {
        params: input_data,
        args: args
    };
    this.httpService.get(final_input_data, success_cb, null);
}

ngOnInit() {
        window['json_functions'].find_activate_link('.MeetingBtnWrapper');
        let req_peram = (window.location + '').split('/');
        let flag = req_peram[req_peram.length - 1];
        this.meeting_type = flag;
        // console.log(flag)
        this.heading = flag + ' Votings';
        this.setStateGetRecords();
    }
    state_name = 'voting_state';
    url_end = 'votings';

    setStateGetRecords(){
        let obj_this = this;
        var state = 'to do';        
        var state_name = obj_this.state_name +'/'+ this.socketService.user_data.id;
        obj_this.state_name = state_name;
        this.socketService.call_backs_on_mode_changed[state_name] = function(){
            if(!window.location.toString().endsWith(obj_this.url_end))
            {
                return;
            }
            state = localStorage.getItem(state_name);            
            if(!obj_this.socketService.admin_mode && state.startsWith('draft'))
            {
                state = 'to do';
                var el1 = $('.StateFilterContainer:first').find('a[state="'+state+'"]');
                el1 = el1[0];            
                obj_this.get_records(el1, state);
            }
        }
        setTimeout(function(){
            if(!obj_this.to_do_only)
            {
                if(localStorage.getItem(state_name))
                {             
                    state = localStorage.getItem(state_name);
                    if(!$('.StateFilterContainer:first').find('a[state="'+state+'"]').length)
                    {
                        state = 'to do';
                    }
                }
            }
            var el = $('.StateFilterContainer:first').find('a[state="'+state+'"]');
            if(el.length)
            {
                el = el[0];
            }
            else{
                state = 'to do';
                el = $('.StateFilterContainer:first').find('a[state="'+state+'"]');
                el = el[0];
            }
            obj_this.get_records(el, state);
        }, 2)
    }
}
