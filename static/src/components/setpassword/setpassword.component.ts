import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../app/http.service';
import {Router} from "@angular/router";
import {ActivatedRoute} from "@angular/router";
declare var $: any;

@Component({
  selector: 'app-setpassword',
  styleUrls:['./setpassword.css'],
  templateUrl: './setpassword.component.html'
})
export class SetpasswordComponent implements OnInit {
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

	constructor(private router: Router, private httpService: HttpService, private route: ActivatedRoute) {}

	submit_password() {
		var obj_this = this;
		var bootbox = window['bootbox'] ;
		if(!obj_this.all_regex.test(this.new_password) && this.new_password != this.confirm_new_password)
		{
			return;
		}
		obj_this.loading = true;
		var token = obj_this.route.snapshot.params.token;
		// var token = new URLSearchParams(window.location.search).get('token');
		// var db = new URLSearchParams(window.location.search).get('db');
		if(!token){
			bootbox.alert('Invalid perameters in set password request. Please contact your admin.');
			return;
		}
        			
        let input_data = {
            token: token,
            password: this.new_password,
        }

		var success_cb = function(result) {
			console.log(result);
			obj_this.loading = false;
			bootbox.alert('Password is successfully updated', function(){
				obj_this.router.navigate(['/login']);
			});
		};
		var failure_cb = function(error) {
			obj_this.error = error;
            obj_this.loading = false;
            console.log(error);
            if(error ==  'Invalid Token')
            {
                error = "Token is already used";
            }
			bootbox.alert(error);			
        };
        

		let args = {
            app: 'authsignup',
            model: 'AuthUser',
            method: 'set_user_password'
        }			
        let final_input_data = {
            params: input_data,
            args: args
        };
        obj_this.httpService.post_public(final_input_data, success_cb, failure_cb);
	}

	ngOnInit() {
		$(document).on('click', '.pass_show .ptxt', function() {
			$(this).text($(this).text() == "Show" ? "Hide" : "Show");
			$(this).prev().attr('type', function(index, attr) {
				return attr == 'password' ? 'text' : 'password';
			});
        });
        $(document).ready(function(){
            setTimeout(function(){
                window['functions'].hideLoader('force');
            },100)
        });
	}
}
