import { Component, OnInit, Input } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { SocketService } from 'src/app/socket.service';
import { NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
import { UserService } from 'src/app/user.service';
declare var $: any;

@Component({
    selector: 'app-roster',
    templateUrl: './roster.component.html',
    styleUrls: ['./roster.component.css']
})

export class RosterComponent implements OnInit {
    @Input() meeting_id: number;
    @Input() meeting_type: string;    
    server_url = window['server_url'];
    httpService: HttpService;
    constructor(private httpServ: HttpService,
            public socketService: SocketService, 
            private activeModal: NgbActiveModal,
            private userServie: UserService) {
                this.httpService = httpServ;
    }    
    attendance_data = [];    
    
    attendees = [];
    db_attendees = [];
    count: number;
    absent_all = false;
    inperson_all = false;
    online_all = false;

    open_dialog(user_id) {
        let obj_this = this;
        // console.log(user_id, 776);
		this.userServie.show_profile_summary(user_id);
    }    

    get_list(){
        let obj_this = this;
        function success(data){
            obj_this.httpService.count = Number(data.total);
            obj_this.count = data.attendees.length;
            obj_this.attendees = data.attendees;
            obj_this.db_attendees = obj_this.attendees;
            obj_this.attendance_data = [];
        }        
        let input_data = {
            meeting_id: obj_this.meeting_id,            
        }
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'get_roster_details'
        }
        let final_input = {
            params: input_data,
            args: args,
            no_loader:1
        }
        
        obj_this.httpService.get(final_input, success, null)
    }

    search_roster(val)
    {
        let obj_this = this;
        if (!val)
        {
            obj_this.attendees = obj_this.db_attendees;
        }
        else
        {
            obj_this.attendees = obj_this.db_attendees.filter((el)=>{
                var mail_matched = false;
                if(el.email && el.email.toLowerCase().indexOf(val) != -1)
                {
                    mail_matched = true;
                }
                var name_matched = false;
                if(el.name && el.name.toLowerCase().indexOf(val) != -1)
                {
                    name_matched = true;
                }
                return mail_matched || name_matched;
            });
        }
    }

    update_attendance(attendee_id: number, val, all_attendees=false){
        let obj_this = this;
        if(!obj_this.socketService.admin_mode)
        {
            return;
        }
        if (!all_attendees)
        {
            if (val == 'absent')
            {
                $('#absent_all').prop('indeterminate', true);
                if (obj_this.inperson_all)
                {
                    $('#inperson_all').prop('indeterminate', true);
                    obj_this.inperson_all = false;
                }
                if (obj_this.online_all)
                {
                    $('#online_all').prop('indeterminate', true);
                    obj_this.online_all = false;
                }
            }
            if (val == 'inperson')
            {
                $('#inperson_all').prop('indeterminate', true);
                if (obj_this.absent_all)
                {
                    $('#absent_all').prop('indeterminate', true);
                    obj_this.absent_all = false;
                }
                if (obj_this.online_all)
                {
                    $('#online_all').prop('indeterminate', true);
                    obj_this.online_all = false;
                }
            }
            if (val == 'online')
            {
                $('#online_all').prop('indeterminate', true);
                if (obj_this.absent_all)
                {
                    $('#absent_all').prop('indeterminate', true);
                    obj_this.absent_all = false;
                }
                if (obj_this.inperson_all)
                {
                    $('#inperson_all').prop('indeterminate', true);
                    obj_this.inperson_all = false;
                }
            }
        }
        let attendee = this.attendance_data.find(x=>x.id == attendee_id);        
        if(attendee)
        {
            attendee.attendance = val; 
        }
        else{
            this.attendance_data.push({id: attendee_id, attendance: val});
        }
        // console.log(this.attendance_data, 103);
    }

    submit_attendance(e){        
        let obj_this = this;
        if (!obj_this.attendance_data || !obj_this.attendance_data.length)
        {
            obj_this.close_roster(e);
            return;
        }
        let input_data = {
            meeting_id: obj_this.meeting_id,
            attendance_data: obj_this.attendance_data,
        }
        // console.log(input_data, 222);
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'mark_attendance'
        }
        let final_input = {
            params: input_data,
            args: args
        }
        // console.log(final_input);
        obj_this.httpService.post(final_input, function(data){
            obj_this.attendance_data = [];
            obj_this.close_roster(data);
        }, null);
    }
    close_roster(data){
        this.activeModal.close(data);
    }
    check_all(el)
    {
        let obj_this = this;
        if(!obj_this.socketService.admin_mode)
        {
            return;
        }
        let target = $(el).closest('.custom-checkbox');
        let new_val = false;
        let attendance = '';
        $('#absent_all').prop('indeterminate', false);
        $('#inperson_all').prop('indeterminate', false);
        $('#online_all').prop('indeterminate', false);
        if(target.hasClass('absent-all'))
        {
            new_val = $('#absent_all').prop('checked');
            new_val = !new_val;
            obj_this.absent_all = new_val;
            obj_this.online_all = false;
            obj_this.inperson_all = false
            attendance = 'absent';
        }

        if(target.hasClass('inperson-all'))
        {
            new_val = $('#inperson_all').prop('checked');
            new_val = !new_val;
            obj_this.inperson_all = new_val;
            $('input[type="radio"].inperson').prop('checked', new_val);
            obj_this.absent_all = false;
            obj_this.online_all = false;
            attendance = 'inperson';
        }

        if(target.hasClass('online-all'))
        {
            new_val = $('#online_all').prop('checked');
            new_val = !new_val;
            obj_this.online_all = new_val;
            $('input[type="radio"].online').prop('checked', new_val);
            obj_this.absent_all = false;
            obj_this.inperson_all = false;
            attendance = 'online';
        }
        if (new_val)
            {
                obj_this.db_attendees.forEach(el => {
                    el.attendance = attendance;
                    obj_this.update_attendance(el.id, attendance, true);
                });
            }
            else
            {
                obj_this.db_attendees.forEach(el => {
                    el.attendance = '';
                    obj_this.update_attendance(el.id, attendance, true);
                });
            }
    }

    ngOnInit() {
        this.get_list();        
    }
}