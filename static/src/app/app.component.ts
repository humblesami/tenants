import { Component } from '@angular/core';
import {SocketService} from './socket.service';
import { UserService } from './user.service';
import { Router } from '@angular/router';
declare var $:any;

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',    
})

export class AppComponent {        
    userService: UserService;

    constructor(private ss: SocketService, userServ: UserService, private router: Router)
    {
        this.userService = userServ;
        console.log(Date()+'-' + new Date().getMilliseconds());
        if(window['site_config'].log_loading)
        {
            console.log('App constructor '+window['dt_functions'].now());
        }
        this.socketService = ss;        
    }
    socketService: SocketService;

	topFunction() {        
		document.body.scrollTop = 0;
		$("html, body").animate({ scrollTop: 0 }, 600);
    }    

	scrollFunction() {
		if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
			document.getElementById("backTop").style.display = "block";
		} else {
			document.getElementById("backTop").style.display = "none";
		}
    }

    change_messenger_view()
    {
        this.socketService.is_messenger_max = true;
    }

    close_messenger_popup(){
        $('.popup.messenger').hide();
    }
    
    odoo_build = window['odoo'] ? 1 : undefined;
    ngOnInit() {
        var obj_this = this;
        window.onscroll = function() {obj_this.scrollFunction()};        
        // console.log(5534);
        $(function(){
            window['functions'].hideLoader('Site Resources');
            // console.log(11777);
        })
    }
}
