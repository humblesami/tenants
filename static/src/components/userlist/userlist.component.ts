import { Component, EventEmitter, OnInit, Input, Output } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { UserService } from 'src/app/user.service';
declare var $: any;

@Component({
    selector: 'app-userlist',
    templateUrl: './userlist.component.html',
    styleUrls: ['./userlist.component.css']
})
export class UserlistComponent implements OnInit {
    @Input() selection_input_str = '';
    @Input() user_input_str = '';
    @Input() add_only = 0;

    @Output() group_users_changed : EventEmitter <any> = new EventEmitter();
    server_url = window['site_config'].server_base_url;
    constructor(private httpService: HttpService,
        public userService: UserService) {
            
    }
    shown_users = [];
    all_users = [];
    selection_input = [];
    count: number = 0;
    available_user_count = 0;
    selected_user_count = 0;

    
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
            obj_this.selected_user_count = obj_this.selection_input.length;
            obj_this.group_users_changed.emit(obj_this.selection_input);            
        }
        if(obj_this.user_input_str)
        {
            obj_this.all_users = JSON.parse(obj_this.user_input_str);
            if (obj_this.all_users.length)
            {
                obj_this.all_users = JSON.parse(obj_this.user_input_str);
                obj_this.all_users.forEach((val)=>{
                    if (!val.selected)
                    {
                        val.selected = obj_this.check_user_selected(val.id);
                    }
                });
                obj_this.shown_users = obj_this.all_users;
                obj_this.count = obj_this.all_users.length;
                obj_this.available_user_count = obj_this.count - obj_this.selected_user_count;
                return;
            }
        }

        function success(data){            
            obj_this.httpService.count = Number(data.total);
            obj_this.count = data.users.length;
            obj_this.available_user_count = obj_this.count - obj_this.selected_user_count;
            obj_this.all_users = data.users;
            obj_this.all_users.forEach((val)=>{
                val.selected = obj_this.check_user_selected(val.id);
            });
            obj_this.shown_users = obj_this.all_users;
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
        this.available_tab = 0;
    }

    all_selected_users(el)
    {   
        let obj_this = this;     
        obj_this.shown_users = obj_this.all_users.filter((el)=>{
            return el.selected == true;
        });
        obj_this.activate_tab(el);        
    }

    available_tab = 0;

    all_available_users(el)
    {
        let obj_this = this;
        obj_this.shown_users = obj_this.all_users.filter((el)=>{
            return el.selected == false;
        });
        obj_this.activate_tab(el);
        this.available_tab = 1;
    }

    all_profile_users(el)
    {
        let obj_this = this;
        obj_this.shown_users = obj_this.all_users;
        obj_this.activate_tab(el);
    }

    toggle_user_selection(obj){
        let obj_this = this;
        obj.selected = !obj.selected;
        let selection_output = obj_this.all_users.filter((el)=>{
            return el.selected == true;
        });
        obj_this.selected_user_count = selection_output.length;
        obj_this.available_user_count = obj_this.count - obj_this.selected_user_count;
        obj_this.group_users_changed.emit(selection_output);
    }

    user_serach(val)
    {
        let obj_this = this;
        let btn_text = $('a.btn.active').text();
        if (btn_text.toLowerCase().indexOf('all') != -1)
        {
            obj_this.all_profile_users($('a.btn.active'));
        }
        else if (btn_text.toLowerCase().indexOf('available') != -1)
        {
            obj_this.all_available_users($('a.btn.active'));
        }
        else if (btn_text.toLowerCase().indexOf('selected') != -1)
        {
            obj_this.all_selected_users($('a.btn.active'));
        }
        //Shown users are set above (taken from all users)
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

    uncheck_user(user_obj)
    {
        user_obj.selected = false;
    }
    check_user(user_obj)
    {
        user_obj.selected = true;
    }

    ngOnInit() {        
        this.get_list();        
    }
}