import { Component, OnInit } from "@angular/core";
import { SocketService } from "../../app/socket.service";
declare var $: any;

@Component({
    selector: "app-chat",
    styleUrls:['./notification.css'],
	templateUrl: "./chat.component.html",
})
export class ChatComponent implements OnInit {
	socketService : SocketService;
    constructor(
		private ss: SocketService) {
		var obj_this = this;
        obj_this.socketService = ss;
    }
    odoo_build = window['odoo'] ? 1 : undefined;

	close_right_panel() {
		$(".right-panel").hide();
    }

    toggle_notifications(e)
    {
        var togglerelated = window['functions'].togglerelated;
        togglerelated('.container.notification-list'); 
    }

    mark_notifications_read(li){        
        let obj_this = this;
        if(li.html().trim() == 'No New Notifications')
        {
            return;
        }
        let item = obj_this.socketService.notificationList[li.index()];
        if(!item)
        {
            return;
        }
        if(!item.id){
            return;
        }
        var options =
        { 
            data:{
                params: {
                    notification_id: item.id,
                },
                args : {
                    app: 'chat',
                    model: 'Notification',
                    method: 'mark_read'
                }                
            },
            onSuccess:function(read_notification_ids){
                for(var i in read_notification_ids)
                {
                    let notificationList = obj_this.socketService.notificationList;
                    let notif_count = notificationList.length;
                    for(var j=0; j < notif_count; j++)
                    {
                        if(read_notification_ids[i] == notificationList[j].id)
                        {
                            obj_this.socketService.remove_item_from_notification_list(j);
                            break;
                        }
                    }
                }
            }
        }
        window['dn_rpc_object'](options);
    }

	ngOnInit() {
        var obj_this = this;
        var route = window['pathname'];        
        $('body').on('click', '.notification-list li', function(){                        
            var url = $(this).find('a').attr('link');
            if(!url)
            {
                url = $(this).find('a').attr('href');
                if(!url){
                    console.log('Invalid url')
                    return;
                }
            }
            if(!url.startsWith('http'))
            {
                if(!url.startsWith('/'))
                {
                    url = '/'+url;
                }
            }
            obj_this.mark_notifications_read($(this));
            // console.log(url);
            window.location = url;
        });
        if(route == '/chat')
        {            
            //console.log("Loaded as route");
            $('body').css('background-color','transparent');
            $('.main-user-navbar').css({'padding-top': '8px'});
        }
        else
        {
            //console.log("Loaded in app");
        }
    }
}