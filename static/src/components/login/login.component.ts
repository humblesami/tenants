import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpService } from '../../app/http.service'
import {SocketService} from "../../app/socket.service";
declare var $:any;

@Component({
    templateUrl: 'login.component.html',
    styleUrls:['./login.component.css'],
})
export class LoginComponent implements OnInit {
    selectedFile: FileReader = null;
    loading = false;
    submitted = false;
    returnUrl: string;
    error: string;
    page_loaded = false;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,        
        private httpService: HttpService,
		private socketService: SocketService) {
            
        }

    ngOnInit() {        
        $('body').show();
        this.socketService.user_data = undefined;        
        $(document).ready(function(){
            setTimeout(function(){
                window['functions'].hideLoader('force','login');                
            },100);
        });
        var path_name = window['pathname'];
        if(path_name == '/logout')
        {
            window['current_user'].logout();
        }
        this.page_loaded = true;
        window['sign_loaded'] = undefined;
        window['voting_id'] = -1;
    }
    

    onSubmit() {
        this.submitted = true;
        this.loading = true;
        let obj_this = this;
        obj_this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';

        let req_url = '/ws/authenticate-json';
        let input_data = {
            login: $('#username').val(),
            password: $('#password').val(),
        };
        input_data['app_name'] = window['site_config'].app_name;
        var success_cb = function (user) {
            obj_this.socketService.connect_socket(user);
            obj_this.loading = false;
            obj_this.router.navigate([obj_this.returnUrl]);
        };
        var failure_cb = function (error) {
            if(typeof(error) != 'string')
            {
                error ='Could not connect to server';
            }            
            obj_this.error = error;
            obj_this.loading = false;
            $('body').find('button[type="submit"]:first').removeAttr('disabled');
            $('body').find('.login-feedback').html(error);
            $('#server-wait').hide();
        };
        var complete_cb = function(){
            obj_this.loading = false;
        };
        this.httpService.authenticate(req_url, input_data, success_cb, failure_cb, complete_cb);
    }
}
