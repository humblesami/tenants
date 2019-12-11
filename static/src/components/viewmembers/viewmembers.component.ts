import { Component, OnInit, Input } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { SocketService } from 'src/app/socket.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { UserService } from 'src/app/user.service';

declare var $: any;

@Component({
    selector: 'app-viewmembers',
    templateUrl: './viewmembers.component.html',
    styleUrls: ['./viewmembers.component.css']
})
export class ViewmembersComponent implements OnInit {
    @Input() selection_input_str = '';
    @Input() user_input_str = '';
    @Input() title = '';

  // @Output() group_users_changed : EventEmitter <any> = new EventEmitter();
    server_url = window['server_url'];
    httpService: HttpService;
    constructor(private httpServ: HttpService,
        private userService: UserService,
        private socketService: SocketService,public activeModal: NgbActiveModal) {
        this.httpService = httpServ;
    } 

    shown_users = [];
    all_users = [];
    selection_input = [];
    count: number;

    show_profile_summary(user_id)
    {
        this.userService.show_profile_summary(user_id);
    }
    
    check_user_selected(user_id)
    {
        let selected = false;
        for (const user of this.selection_input) {
            if (user.id == user_id)
            {
                selected = true;
                break;
            }
        }
        return selected;
    }

    get_list(){
        let obj_this = this;        
        if(obj_this.selection_input_str)
        {
            obj_this.selection_input = JSON.parse(obj_this.selection_input_str);
            // obj_this.group_users_changed.emit(obj_this.selection_input);            
        }
        if(obj_this.user_input_str)
        {
            obj_this.all_users = JSON.parse(obj_this.user_input_str);
            // console.log(obj_this.all_users, 223);
            obj_this.all_users.forEach((val)=>{
                if (!val.selected)
                {
                    val.selected = obj_this.check_user_selected(val.id);
                }
            });
            this.shown_users = this.all_users;
            return;
        }

        function success(data){            
            obj_this.httpService.count = Number(data.total);
            obj_this.count = data.users.length;
            obj_this.all_users = data.users;
            obj_this.all_users.forEach((val)=>{
                val.selected = obj_this.check_user_selected(val.id);
            });
            this.shown_users = this.all_users;
        }
        let args = {
            app: 'meetings',
            model: 'Profile',
            method: 'get_all_users'
        }
        let final_input = {
            params: {},
            args: args,
            no_loader:1
        }
        
        obj_this.httpService.get(final_input, success, (er)=>{console.log(er);})
    }

    activate_tab(el){
        $('.user-types:first>a').removeClass('active');
        $(el).addClass('active');
    }


    // toggle_user_selection(obj){
    //     obj.selected = !obj.selected;
    //     let selection_output = this.all_users.filter((el)=>{
    //         return el.selected == true;
    //     });
    //     // this.group_users_changed.emit(selection_output);
    // }

    user_serach(val)
    {
        let obj_this = this;
        if (!val)
        {
            obj_this.shown_users = obj_this.all_users;
            return;
        }
        obj_this.shown_users = obj_this.shown_users.filter((el)=>{
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
    
    ngOnInit() {        
        this.get_list();
    }
}