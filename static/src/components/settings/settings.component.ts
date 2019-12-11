import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../app/http.service';
import {Router} from "@angular/router";

declare var $: any;

@Component({
    selector: 'app-settings',
    styleUrls:['./settings.css'],
    templateUrl: './settings.component.html'
})
export class SettingsComponent implements OnInit {
    old_password = '';
    new_password = '';
    confirm_new_password = '';
    loading = false;
    error: string;
    valid = false;
	all_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@~`!@#$%^&*()_=+\\';:"\/?>.<,-])(?=.{8,})/
	lower_regex = /^(?=.*[a-z])/
	uper_regex = /^(?=.*[A-Z])/
	numeric_regex = /^(?=.*[0-9])/
	special_regex = /^(?=.*[@~`!@#$%^&*()_=+\\';:"\/?>.<,-])/
	min_length_regex = /^(?=.{8,})/

    constructor(private router: Router, private httpService: HttpService) {}

    submit_password() {
        var bootbox = window['bootbox'];
        if(!window['site_config'].is_localhost)
        {
            if(!this.old_password)
            {
                bootbox.alert('Please provide your previous password.')
                return;
            }
            if(!this.all_regex.test(this.new_password) || this.new_password != this.confirm_new_password)
            {
                bootbox.alert('Please follow the rules to set your new password.')
                return;
            }
        }
		
        var obj_this = this;
        this.loading = true;
        let input_data = {
            args:{
                app: 'authsignup',
                model:'AuthUser',
                method:'change_password',
            },
            params:{
                old: this.old_password,
                new: this.new_password,                
            }
        };

        var success_cb = function(result) {
            obj_this.loading = false;
			bootbox.alert('Password is successfully updated');
            window["functions"].go_to_login();            
        };
        var failure_cb = function(error) {
            obj_this.error = error;
            obj_this.loading = false;
			bootbox.alert('Something went wrong, Please try in some time');
            console.log(error);
        };
        var complete_cb = function() {
            obj_this.loading = false;
        };
        this.httpService.post(input_data, success_cb, failure_cb);
    }

    ngOnInit() {
        $(document).on('click', '.pass_show .ptxt', function() {
            $(this).text($(this).text() == "Show" ? "Hide" : "Show");
            $(this).prev().attr('type', function(index, attr) {
                return attr == 'password' ? 'text' : 'password';
            });
        })
    }
}
