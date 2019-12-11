import { Injectable, NgZone } from '@angular/core';
import { VideoCall } from '../app/models/video_call';
import { Router, ActivatedRouteSnapshot } from "@angular/router";
import { ChatGroup, ChatUser, AppUser, ChatClient } from '../app/models/chat';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
declare var $;


@Injectable()
export class SocketService {

    io: any;
    socket:any;
    user_data: AppUser;
    chat_clients: Array<ChatClient>;
    chat_groups: Array<ChatGroup>;
    chat_users: Array<ChatUser>;
    server_url = '';
    media_url = '';
    user_photo = '';
    on_verified = [];
    verified = false;
    iframe_url = true;
    not_public_url = 0;
    server_events = {};
    unseen_messages = 0;
	notificationList = [];
    current_id = undefined;
    site_config = undefined;
    current_model = undefined;
    video_call : VideoCall;
    is_messenger_max = false;
    site_url = '';
    rtc_multi_connector : any;
    messenger_active = 0 ;
    active_route_snapshot : ActivatedRouteSnapshot;
    search_bar_shown = false;

    get_user_by_id(uid:number){
        return this.chat_users.find(function(item){
            return item.id == uid;
        })
    }

    constructor(private router: Router
        , private modalService: NgbModal
        , public zone: NgZone
        ) {
        window['dynamic_files'] = []
        var obj_this = this;
        this.site_config = window['site_config'];
        this.site_url = this.site_config.site_url;
        // console.log(this.site_url);
        obj_this.video_call = new VideoCall(obj_this);

        if(!window['socket_manager'])
        {
            window['socket_manager'] = obj_this;
            // console.log(obj_this, 342);
        }
        obj_this.chat_users = [];
        obj_this.server_url = obj_this.site_config.server_base_url;
        obj_this.media_url = obj_this.server_url + '/media';
        var res = window['auth_js'].is_public_route();
        if(!res)
        {
            try
            {
                var user_cookie = localStorage.getItem('user');
                let cuser = undefined;
                if(user_cookie)
                {
                    cuser = JSON.parse(user_cookie);
                }
                else
                {
                    window['functions'].go_to_login();
                    return;
                }
                // console.log(cuser, 1997);
                if(cuser && cuser.token)
                {
                    obj_this.connect_socket(cuser);
                }
                else
                {
                    window['functions'].go_to_login();
                    return;
                }
            }
            catch(er)
            {
                console.log('Failed socket exception ',er)
            }
        }
        else
        {
            $('#main-div').show();
        }
    }

    call_backs_on_mode_changed = {};
    on_admin_mode_changed(){
        let obj_this = this;
        for(let fun_name in obj_this.call_backs_on_mode_changed)
        {
            if(obj_this.call_backs_on_mode_changed[fun_name])
            {
                obj_this.call_backs_on_mode_changed[fun_name]();
            }
        }
    }

    route_changed(route: ActivatedRouteSnapshot){
        this.active_route_snapshot = route;
    }

    admin_mode = false;
    actually_admin = false;
    connect_socket(authorized_user){
        var obj_this = this;
        if(!authorized_user)
        {
            console.log('Not authorized');
            return;
        }
        if(!authorized_user.photo)
        {
            this.user_photo = this.media_url + '/profile/default.png';
        }
        else{
            this.user_photo = this.server_url + authorized_user.photo;
        }
        // console.log(authorized_user, obj_this.user_photo, 1355);
        let me = {
            id:authorized_user.id,
            group: undefined
        }
        // console.log(authorized_user.groups);
        if(!authorized_user.groups)
        {
            authorized_user.groups = [];
        }
        obj_this.actually_admin = false;
        if(authorized_user.groups.length > 0)
        {
            me.group = authorized_user.groups[0].name;
            var admin_group = authorized_user.groups.filter(function(item){return item.name == 'Admin' })            
            if(admin_group.length)
            {
                obj_this.actually_admin = true;
            }
        }
        // console.log(me);
        $('#main-div').show();        
        var admin_mode_cookie = localStorage.getItem('admin_mode');
        if (!admin_mode_cookie)
        {
            localStorage.setItem('admin_mode', JSON.stringify({admin_mode: false}));
            obj_this.admin_mode = false;
        }
        else if (!obj_this.actually_admin)
        {
            localStorage.setItem('admin_mode', JSON.stringify({admin_mode: true}));
            obj_this.admin_mode = false;
        }
        else
        {
            let admin_mode_obj = JSON.parse(admin_mode_cookie);
            obj_this.admin_mode = admin_mode_obj['admin_mode'];            
        }
        obj_this.user_data = authorized_user;


        let complete_server_url = obj_this.site_config.chat_server+'/sio';
        obj_this.socket = window['io'].connect(complete_server_url,{
            reconnection: false,
            transports: ['websocket'],
            reconnectionDelay: 2000,
            reconnectionDelayMax : 5000,
            reconnectionAttempts: 2,
        }).on('connect_error', function (err) {
            console.log('Socket connection failed '+complete_server_url+' please run socket server is up');
        });
        obj_this.socket.on('connect',function(){
            obj_this.socket.off('server_event');
            // console.log(343232);
            authorized_user.socket_id = obj_this.socket.id;
            authorized_user.web_server_url = window['server_url'];
            var socket_error = "Socket connection not established at "+ obj_this.site_config.chat_server + ' because ';
            var options = {
                url: obj_this.site_config.chat_server+'/verify_socket',
                data: authorized_user,
                success: function(data){
                    if(data && !data.error)
                    {
                        socket_error = '';
                        onAuthenticated(data.data);
                    }
                    else if(data.error)
                    {
                        // obj_this.user_data = undefined;
                        // console.log(data.error+' for ', authorized_user);
                        socket_error += data.error;
                    }
                    else
                    {
                        socket_error += ' no response';
                    }
                },
                error:function(a, b){
                    socket_error += b.responseText;
                },
                complete:function(){
                    if(socket_error)
                    {
                        console.log(socket_error);
                    }
                }
            };
            $.ajax(options);

            function onAuthenticated(data) {
                // console.log(1116, data.notifications.list, 83433);
                if(!data.user)
                {
                    console.log('Invalid user data', data);
                }
                if(data.message)
                {
                    console.log(data.message.error);
                }
                if(data.user && data.friends)
                {

                }
                else{
                    console.log('invalid user data ', data);
                    return;
                }
                // console.log("Authenticated\n\n");
                // console.log(obj_this.user_data, 1344);
                localStorage.setItem('user', JSON.stringify(obj_this.user_data));
                obj_this.verified = true;
                if(!data.unseen && data.unseen != 0)
                {
                    data.unseen = 0;
                    console.log('Please ask to add unseen attribute from service developer of get_user_data');
                }

                obj_this.unseen_messages = data.unseen;
                obj_this.chat_clients = new Array<ChatClient>();
                for(var grp of data.chat_groups)
                {
                    obj_this.chat_clients.push(grp);
                }
                data.friends = window['js_utils'].sort_by_two_keys(data.friends);
                for(var frd of data.friends)
                {
                    obj_this.chat_clients.push(frd);
                }
                obj_this.chat_groups = data.chat_groups;
                obj_this.chat_users = data.friends;

                // console.log(obj_this.chat_users, 4509);

                obj_this.notificationList = [];
                data.notifications = data.notifications.list;
                for(let i in data.notifications)
                {
                    obj_this.add_item_in_notification_list(data.notifications[i], null);
                }
                // console.log(1111, obj_this.notificationList);
                obj_this.notificationList = obj_this.notificationList.reverse();
                obj_this.registerEventListeners();
                for(let i in obj_this.on_verified)
                {
                    obj_this.on_verified[i]();
                }
                obj_this.on_verified = [];
            };
            obj_this.socket.on('server_event', function(res){
                try{
                    // console.log(res.name);
                    if(!obj_this.server_events[res.name])
                    {
                        if(!obj_this.verified)
                        {
                            obj_this.execute_on_verified(function(){
                                obj_this.server_events[res.name](res.data);
                            });
                        }
                        else
                        {
                            console.log('Not handeled ', res.name);
                        }
                    }
                    else
                        obj_this.server_events[res.name](res.data);

                }
                catch(er)
                {
                    console.log(er.message, ' in '+res.name+' with data ', res);
                }
            });
        });
    }

    set_admin_mode(mode)
    {
        let obj_this = this;
        obj_this.admin_mode = mode;
        localStorage.setItem('admin_mode', JSON.stringify({admin_mode:mode}));
        obj_this.zone.run(() => obj_this.admin_mode = mode);
        obj_this.on_admin_mode_changed();
    }

    add_chat_user(chat_cleint: ChatClient)
    {
        this.chat_users.push(chat_cleint);
    }

    execute_on_verified = function(method){
        if(this.verified)
            method();
        else
        {
            this.on_verified.push(method);
        }
    }

    update_unseen_message_count(event, target: ChatClient) {
        if(!target)
        {
            console.log('Selection failed for', target);
            return;
        }
        if(!target.unseen && target.unseen != 0)
        {
            target.unseen = 0;
            console.log('Please ask to add unseen attribute for each friend from service developer of get_user_data');
        }
		var inc = 0;
        var obj_this = this;
		try {
            switch (event) {
                case "receive-new-message":
                    inc = 1;
                    break;
                case "read-new-message":
                    inc = -1;
                    break;
				case "user-selected":
					inc = target.unseen * -1;
                    break;
            }

            target.unseen = target.unseen + inc;
			obj_this.unseen_messages = obj_this.unseen_messages + inc;

            if (obj_this.unseen_messages >= 1) {
				$('.un-read-msg.count').show();
			}
			else if (obj_this.unseen_messages <= 0) {
				$('.un-read-msg.count').hide();
			}
		} catch (er) {
			console.log("update message count err no ", er);
		}
    }

	registerEventListeners(){
        var obj_this = this;
        var bootbox = window["bootbox"];

        obj_this.server_events['meeting_started'] = function (res) {
            bootbox.alert(res);
        };

        obj_this.server_events['notification_received'] = function (res) {
            obj_this.add_item_in_notification_list(res, 1);
        };

        obj_this.server_events['notification_updated'] = function (res) {
            console.log('notifications updated')
        };

        obj_this.server_events['incoming_call'] = function (data){
            obj_this.video_call.show_incoming_call(data);
        };
        obj_this.server_events['cancelled'] = function(data){
            obj_this.video_call.cancelled(data);
        };
        obj_this.server_events['call_terminated'] = function(data){
            obj_this.video_call.terminated(data);
        };
        obj_this.server_events['rejected'] = function(data){
            obj_this.video_call.rejected(data);
        };
        obj_this.server_events['accepted'] = function(data){
            obj_this.video_call.accepted(data);
        };
        obj_this.server_events['started_by_caller'] = function(data){
            obj_this.video_call.started_by_caller(data);
        };


        obj_this.server_events['error'] = function (res) {
            if(res == 'Invalid Token')
            {
                console.log('Unauthorized due to invalid token');
                window["functions"].go_to_login();
                return;
            }
            else
                console.log("Error from chat ", res);
        };

        obj_this.server_events['force_log_out'] = function (res) {
            var href = window.location.toString();
            if(href.indexOf('172.16') == -1 || href.indexOf('localhost') == -1)
            {
                window["functions"].go_to_login();
                return;
            }
        };

        obj_this.server_events['point_comment_received'] = function (data) {
            if(window['on_annotation_comment_received'])
            {
                window['on_annotation_comment_received'](data);
            }
        };
    };
    
    user_selection_dialog(dialog_options){
        let obj_this = this;
        var selected_users = [];
        if(dialog_options.selected_users && dialog_options.selected_users.length)
        {
            dialog_options.selected_users.forEach(function(usr){
                selected_users.push({
                    id: usr.id,
                    name: usr.name,
                    email: '',
                    image: usr.photo,
                })
            });
        }

        const modalRef = obj_this.modalService.open(dialog_options.component, { backdrop: 'static', keyboard: false });
        let user_cookie = localStorage.getItem('user');
        let cuser = undefined;
        if(user_cookie)
        {
            cuser = JSON.parse(user_cookie);
        }
        let owner = false;
        let default_selected = false;
        if (dialog_options.owner)
        {
            default_selected = true;
            owner = dialog_options.owner;
        }
        if(dialog_options.user_list && dialog_options.user_list.length)
        {
            if (cuser)
            {
                dialog_options.user_list.filter((el)=>{
                    if (el.id==cuser.id)
                    {
                        el.current_user = owner;
                        el.selected = default_selected;
                    }
                });
            }
            
        }
        else
        {
            dialog_options.user_list = [];
            if (obj_this.chat_users.length)
            {
                for(var usr of obj_this.chat_users)
                {
                    dialog_options.user_list.push({
                        id: usr.id,
                        name: usr.name,
                        email: '',
                        image: usr.photo,
                    })
                }
                if (cuser)
                {
                    dialog_options.user_list.unshift({
                        id: cuser.id,
                        name: cuser.name,
                        email: cuser.email,
                        image: cuser.photo,
                        current_user: owner,
                        selected: default_selected
                    })
                }
            }
        }
        
        modalRef.componentInstance.user_input_str = JSON.stringify(dialog_options.user_list);
        modalRef.componentInstance.selection_input_str = JSON.stringify(selected_users);
        if(dialog_options.extra_input)
        {
            for(var key in dialog_options.extra_input)
            {
                modalRef.componentInstance[key] = dialog_options.extra_input[key];
            }
        }        
        
        if (dialog_options.call_back)
        {
            modalRef.result.then((result) => {
                if (result){
                    dialog_options.call_back(result);
                }
            });
        }
    }

    emit_rtc_event(event_name, data, audience)
    {
        data = {
            name: event_name,
            audience: audience,
            data: data
        }
        this.socket.emit('client_event', data);
    }

	emit_server_event(input_data, args) {
        try{
            var options =
            {
                data:{
                    params: input_data,
                    args : args
                }
            }
            window['dn_rpc_object'](options);
        }
        catch(er)
        {
            console.log(er)
        }
	}

    current_path = '/';
    init_route(url){
        this.not_public_url = 0;
        this.current_id = undefined;
        this.current_model = undefined;
        this.current_path = url;
        this.notificationList.forEach(function(el, i){
            el.active = undefined;
        });
    }

    activate_notification(){

    }

    find_notification_index(res_model, res_id) {
        let index = -1;
        for(let i in this.notificationList){
            let item_in_list = this.notificationList[i];
            if(item_in_list.res_model == res_model && item_in_list.res_id == res_id)
            {
                index = parseInt(i);
                break;
            }
        }
        return index;
    }

    set_notification_text(item){
        let obj_this = this;
        if (obj_this.user_data.id in item.senders)
        {
            item.senders = item.senders[obj_this.user_data.id]
            item.senders = item.senders.filter(function(obj){
                return obj.id != obj_this.user_data.id;
            });
            let count = item.senders.length;
            let senders = item.senders[0].name;

            for(var i=1; i<count -1;i++)
            {
                senders +=', '+item.senders[i].name;
            }
            if(count > 1)
            {
                senders += ' and '+item.senders[count -1].name;
            }
            item.body = senders +' '+item.body;
        }
    }

    add_item_in_notification_list(item, on_receive) {
        var obj_this = this;
        try{
            if(!item.body)
            {
                console.log(item, ' no body');
                return;
            }
            item.body = item.body.trim();
            if(item.body.length == 0)
            {
                console.log('Not notif text in',item);
                return;
            }
        }
        catch(er){
            console.log(er, 'Invalid notif text '+item.body);
            return;
        }

        let route = obj_this.model_routes[item.address.res_app][item.address.res_model];
        if (item.address.info){
            if(item.address.info.file_type)
            {
                route = '/'+ item.address.info.file_type + route + '/';
            }
            route += item.address.info.post_parent_id+'/';
        }
        if(route.indexOf('doc/')> -1)
        {
            item.link =  '/#' + route + item.address.res_id;
        }
        else{
            item.client_route = route + item.address.res_id;
        }
        // item.counter = 1;
        // obj_this.set_notification_text(item);
        if(!item.count)
        {
            item.count = 1;
        }
        var in_list = false;
        if(on_receive)
        {
            for(var i in obj_this.notificationList)
            {
                if(item.id == obj_this.notificationList[i].id)
                {
                    obj_this.notificationList[i].body = item.body;
                    item.count += 1;
                    in_list = true;
                    break;
                }
            }
        }
        if(!in_list)
        {
            if(on_receive)
            {
                obj_this.notificationList.unshift(item);
            }
            else{
                obj_this.notificationList.push(item);
            }
        }
    }

    remove_item_from_notification_list(i) {
        this.notificationList.splice(i, 1);
        setTimeout(function(){
            $('.notif:first').click();
            setTimeout(function(){
                $('.notif:first').click();
            }, 5);
        }, 10);
    }

    get_param(name, url)
    {
        try{
            if (!url) url = location.href;
            name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
            var regexS = "[\\?&]"+name+"=([^&#]*)";
            var regex = new RegExp( regexS );
            var results = regex.exec( url );
            var result = results[1];
            return result;
        }
        catch(er){
            return '';
        }
    }

    model_routes = {
        'meetings':{
            'Event':'/meeting/',
        },
        'voting':{
            'Voting':'/voting/'
        },
        'documents':{
            'PointAnnotation': '/doc'
        }
    }

    close_socket(){
        var socket = window['socket_manager'].socket;
		if(socket && socket.connected){
			socket.disconnect();
            socket = false;
            this.messenger_active = 0;
        }
        this.user_data = undefined;
    }
}
