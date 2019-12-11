import { Component, OnInit } from '@angular/core';
import {DomSanitizer} from "@angular/platform-browser";
import {HttpService} from "../../app/http.service";
import {Location} from '@angular/common';
import { AppUser, ChatGroup, BaseClient, ChatClient, Message, ChatUser } from '../../app/models/chat';
import {SocketService} from "../../app/socket.service";
import { Router } from '@angular/router';
import { ChatgroupComponent } from '../chatgroup/chatgroup.component';
import { ViewmembersComponent } from '../viewmembers/viewmembers.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { MovetomyfolderComponent } from '../movetomyfolder/movetomyfolder.component';
import { UserService } from 'src/app/user.service';
declare var $: any;

@Component({
	selector: 'app-messenger',
	styleUrls:['./messenger.css'],
	templateUrl: './messenger.component.html'
})
export class MessengerComponent implements OnInit {	    
    socketService : SocketService;
	is_minimize = true;
	chat_initilized = 0;
    searchVal = '';
    user: AppUser;
    group_state = '';
    is_request_sent = true;
    people_list: Array<ChatUser>;
    selectedPeople : Array<ChatUser>;

	constructor(
        private sanitizer: DomSanitizer,
        public router: Router,
        private _location: Location,
		private httpService: HttpService,
        private ss: SocketService,
        public userServie: UserService,
        private modalService: NgbModal

        ) {
            // console.log('Recodd');
            window['app_libs']['emoji_picker'].load();            
            window['app_libs']['rtc'].load();
            var obj_this = this;
            obj_this.socketService = ss;            
            var socketService = ss;
            function registerChatEventListeners()
            {
                obj_this.user = socketService.user_data;
                socketService.server_events['chat_group_created'] = function(created_group)
                {
                    if(created_group.owner.id != obj_this.socketService.user_data.id)
                    {
                        console.log("owner should not receive this, please fix it");
                        obj_this.socketService.chat_groups.push(created_group);
                    }
                }
                socketService.server_events['chat_message_received'] = function (msg) {
                    try{
                        // console.log(msg, 'chat_message_received');
                        obj_this.receiveMessage(msg, msg.sender.id);
                    }
                    catch(er)
                    {
                        console.log(er);
                    }
                }

                socketService.server_events['group_chat_message_received'] = function(msg){
                    try{
                        //console.log('redifen chat_message_received');
                        obj_this.receiveGroupMessage(msg, msg.sender.id);
                    }
                    catch(er)
                    {
                        console.log(er);
                    }
                };

                socketService.server_events['friend_joined'] = updateUserStatus;

                socketService.server_events['user_left'] = updateUserStatus;

                socketService.server_events['new_friend'] = function(friend: ChatClient){
                    socketService.chat_users.push(friend);
                }
                socketService.server_events['friend_removed'] = function(friend_id){
                    for(var i = 0; i < socketService.chat_users.length; i++)
                    {
                        if(socketService.chat_users[i].id == friend_id)
                        {
                            socketService.chat_users.splice(i, 1);
                            break;
                        }
                    }
                }
                
                function updateUserStatus(user: ChatClient)
                {                
                    if(obj_this.user.id == user.id)
                    {
                        console.log(user , "Should never happen now");
                        return;
                    }
                    var i = 0;
                    var item_index = -1;
                    var filteredObj = undefined;
                    for(var item of socketService.chat_users)
                    {
                        if(item.id == user.id)
                        {
                            filteredObj = item;
                            item_index = i;
                            break;
                        }
                        i++;
                    }
                    if(item_index == -1){
                        console.log(user , " not found");
                        return;
                    }
                    var new_idex = socketService.chat_users.length - 1;
                    let client = filteredObj as ChatClient;
                    if(user.online)
                    {
                        new_idex = 0;
                        window['js_utils'].move_element(socketService.chat_users, item_index, new_idex);
                    }
                    else{
                        window['js_utils'].move_element(socketService.chat_users, item_index, new_idex);
                    }
                    // console.log(user.online, item_index)
                    client.online = user.online;
                }

                socketService.server_events['chat_group_members_updated'] = function(data){
                    var index = -1;
                    var all_groups = obj_this.socketService.chat_groups;
                    for(var i =0; i < all_groups.length; i++)
                    {
                        if(all_groups[i].id == data.id)
                        {
                            index = i;
                            break;
                        }
                    }
                    if(index == -1)
                    {
                        console.log('members added in valid group', data, obj_this.socketService.chat_groups);
                        obj_this.on_messge_from_new_group(data.id);
                        return;
                    }
                    var group = undefined;
                    if(obj_this.active_chat_user && obj_this.active_chat_user.is_group && obj_this.active_chat_user.id == data.id)
                    {
                        group = obj_this.active_chat_user as ChatGroup;                    
                    }
                    else
                    {
                        group = obj_this.socketService.chat_groups[index];
                    }
                    for(var j=0;j<data.members.length;j++)
                    {
                        group.members.push(data.members[i]);
                    }
                }
                
                obj_this.people_list = new Array<ChatUser>();            
                for(var ind in obj_this.socketService.chat_users)
                {
                    let obj_user = obj_this.socketService.chat_users[ind] as ChatUser;                
                    obj_this.people_list.push(obj_user);
                }
                if(!obj_this.user)
                {
                    console.log("No user data is socket service yet");
                    return;
                }
            }
            try{                
                ss.execute_on_verified(registerChatEventListeners);
            }
            catch(er)
            {
                console.log(113, er);
            }        
    }

    scrollToEnd(){
        $('.msg_card_body').scrollTop($('.msg_card_body')[0].scrollHeight);
    }

    group_name = '';
    add_message(chat_client: ChatClient, message: Message){
        chat_client.messages= this.add_attachment(chat_client.messages,message);
        // chat_client.messages.push(message);      
        //do above with function
        // console.log(345, chat_client.messages);
    }

    close_group_setup()
    {
        this.switch_group_mode('none');
    }
    
    open_my_folder(evn,doc){

        evn.preventDefault();
        evn.stopPropagation();

        let obj_this = this;
		const modalRef = this.modalService.open(MovetomyfolderComponent, { backdrop: 'static' });
        modalRef.componentInstance.doc_id = doc.id;
        modalRef.componentInstance.member_id = obj_this.user.id;
        modalRef.result.then(function(data){
            if(data){
                doc.moved = true;
                window['bootbox'].alert(data);
            }
            // console.log(data,111113232);
        });
    }    

    change_messenger_view()
    {
        this.socketService.is_messenger_max = false;        
        this._location.back();
        $('.popup.messenger').show();
    }
    
    leave_group(){
        let obj_this = this;
        let input_data = {
            args:{
                app:'chat',
                model:'ChatGroup',
                method:'remove_member'
            },
            params: {
                group_id: obj_this.active_chat_user.id,
                member_id: obj_this.user.id
            }
        }
        obj_this.httpService.post(input_data, function(data){                        
            var all_groups = obj_this.socketService.chat_groups;
            for(var i =0; i < all_groups.length; i++)
            {
                if(all_groups[i].id == input_data.params.group_id)
                {
                    all_groups.splice(i, 1);
                    break;
                }
            }
            obj_this.set_chat_mode('none');
        } , function(){
            console.log('Group members not fetched');
        });
    }

    switch_group_mode(mode: string)
    {
        this.group_mode = mode;
        if(mode == 'none')
        {
            this.selected_chat_group = undefined;
        }
        this.selectedPeople = [];
        // console.log(this.group_mode, this.selected_chat_group);
    }

    create_chat_room()
    {
        let obj_this = this;
        if(!obj_this.group_name)
        {
            console.log('group name required');
            return;
        }
        let input_data= {
            args:{
                app:'chat',
                model:'ChatGroup',
                method:'create'
            },
            params:{
                name: obj_this.group_name,
                members: obj_this.selectedPeople
            }
        }
        obj_this.httpService.post(input_data,function(created_chat_group){
            obj_this.socketService.chat_groups.push(created_chat_group);
            created_chat_group.created_by = obj_this.user;
            obj_this.close_group_setup();
        }, function(){
            
        });
    }
    
    
    start_group_chat(selected_group: ChatGroup, e){
        let obj_this = this; 
        if(e && e.target && $(e.target).hasClass('show_members_btn'))
        {
            return;
        }        
        if(selected_group && !selected_group.is_group)
        {
            selected_group.is_group = true;
        }
        obj_this.switch_group_mode('chat');
        obj_this.activate_chat_user(selected_group);
        // console.log(obj_this.active_chat_user, 155);
        let args = {
            app: 'chat',
            model: 'ChatGroup',
            method: 'get_messages'
        }
        let input_data = {
            params: {group_id: selected_group.id},
            args: args
        };
        var call_on_user_selected_event = function(data){
            if(!Array.isArray(data))
            {
                data = [];
            }
            obj_this.is_request_sent = false;
            obj_this.active_chat_user.messages = [];
            obj_this.onGroupSelected(data);
        }
        input_data['no_loader'] = 1;
        obj_this.httpService.get(input_data, call_on_user_selected_event, call_on_user_selected_event);
    }

    can_edit_group: Boolean;
    group_mode = 'none';
    selected_chat_group: ChatGroup;
    group_create_mode(){
        let obj_this = this;
        obj_this.group_state = 'create';		
		var on_modal_closed = (result) => {            
            obj_this.group_name = result.group_name;
            obj_this.selectedPeople = result.selectd_users;
            obj_this.create_chat_room();            
        };
        var diaolog_options = {
            selected_users: [],
            user_list: [],
            component: ChatgroupComponent,
            extra_input: {},
            call_back: on_modal_closed, 
        };
        obj_this.socketService.user_selection_dialog(diaolog_options);
    }
    
    show_group_members(group: ChatGroup,ev=undefined){
        if(ev){
            ev.preventDefault();
            ev.stopPropagation();
        }
        let obj_this = this;
        obj_this.group_state = 'update'
        obj_this.group_name = group.name;
        let input_data = {
            args:{
                app:'chat',
                model:'ChatGroup',
                method:'get_details'
            },
            params: {
                group_id: group.id
            }
        }
        obj_this.httpService.post(input_data, function(data){
            let is_owner = data.is_owner;
            obj_this.selected_chat_group = data as ChatGroup;
            var all_chat_groups = obj_this.socketService.chat_groups;
            for(var n=0; n < all_chat_groups.length; n++)
            {
                if(all_chat_groups[n].id == data.id)
                {
                    all_chat_groups[n] = data;
                    break;
                }
            }
            var on_modal_closed = function(result){
                obj_this.group_name = result.group_name;
                obj_this.selectedPeople = result.selectd_users;
                obj_this.update_chat_group_members();
            };
            let diaolog_options = {}
            if (is_owner)
            {
                diaolog_options = {
                    selected_users: obj_this.selected_chat_group.members,
                    user_list: [],
                    owner: true,
                    component: ChatgroupComponent,
                    extra_input: {group_name : group.name},
                    call_back: on_modal_closed, 
                };
            }
            else
            {
                diaolog_options = {
                    selected_users: obj_this.selected_chat_group.members,                    
                    extra_input: {title : 'Chat Group : ' + group.name},
                    user_list: obj_this.selected_chat_group.members,
                    component: ViewmembersComponent
                };
            }
            obj_this.socketService.user_selection_dialog(diaolog_options);
            
        } , function(){
            console.log('Group members not fetched');
        });
    }

    update_chat_group_members(){
        let obj_this = this;
        let input_data= {
            args:{
                app:'chat',
                model:'ChatGroup',
                method:'update_members'
            },
            params:{
                group_id: obj_this.selected_chat_group.id,
                members: obj_this.selectedPeople
            }
        }
        obj_this.httpService.post(input_data,function(){
            let all_chat_groups = obj_this.socketService.chat_groups;
            for(var n = 0; n < all_chat_groups.length; n++)
            {
                if(all_chat_groups[n].id == input_data.params.group_id)
                {
                    all_chat_groups[n].members = obj_this.selectedPeople;
                    break;
                }
            }
            
            obj_this.switch_group_mode('none');
        }, function(){

        });
    }
    
	select_chat_user(target: ChatClient) {        
        var obj_this = this;
        obj_this.attachments = [];                
        obj_this.activate_chat_user(target);
        $('.msg_card_body').css('visibility', 'visible');
        this.is_minimize = false;        
        window['app_libs']['rtc'].load();
        if(!obj_this.active_chat_user)
        {
            console.log("No user selected with "+target.id+' from ',obj_this.socketService.chat_users);
            return;
        }
        
        let args = {
            app: 'chat',
            model: 'message',
            method: 'get_friend_messages'
        }
        let input_data = {
            params: {target_id: target.id},
            args: args
        };
        var call_on_user_selected_event = function(data){
            if(!Array.isArray(data))
            {
                data = [];
            }
            obj_this.is_request_sent = false;
            obj_this.active_chat_user.messages = [];
            obj_this.onUserSelected(data);
        }
        input_data['no_loader'] = 1;
        obj_this.httpService.get(input_data, call_on_user_selected_event, call_on_user_selected_event);        
    }
    
    activate_chat_user(chat_client: ChatClient){        
        if(!chat_client.messages)
        {
            chat_client.messages = [];
        }
        this.active_chat_user = chat_client;
        // console.log(chat_client, 1999);
        this.set_chat_mode('active');
    }

    set_chat_mode(mode: string){
        this.chat_mode = mode;
        if(mode == 'none')
        {
            // console.log(mode, 19);
            this.active_chat_user = undefined;
            this.selected_chat_group = undefined;
        }
    }

    clean_member_selection(){
        $('input[role="combobox"]:visible:first').val('');
    }

    chat_mode = 'none';

    scroll_to_end(selector)
    {
        if($(selector).length > 0)
        {
            setTimeout(function(){
                $(selector).stop().animate({
                    scrollTop: $(selector)[0].scrollHeight
                }, 50, function(){
                    setTimeout(function(){
                        $(selector).css('visibility', 'visible');
                    }, 50)                    
                });
            }, 50);
        }
        else
        {
            console.log('Invalid selector '+selector+' to scroll');
        }
    }

    message_limit = 20;
    message_offset = 0;
    active_chat_user: ChatClient;

    onGroupSelected(messages: Array<Message>, already_fetched = 0) {
        var obj_this = this;
        $( ".msg_card_body").unbind( "scroll" );
        obj_this.message_offset = 0;
        obj_this.active_chat_user.read = false;
		$(".msg_card_body").scroll(function(){
            let scroll_top = $(".msg_card_body").scrollTop();
            if(!obj_this.active_chat_user)
            {
                console.log('Invalid chat user');
                return;
            }
            if(!obj_this.active_chat_user.messages)
            {
                // console.log('No chat user messages');
                obj_this.active_chat_user.messages = [];                
            }
			if(scroll_top < 2){
                get_group_old_messages();
			}
        });


        function get_group_old_messages(){
            if(obj_this.active_chat_user.messages.length <= obj_this.message_limit)
            {
                return;
            }
            obj_this.is_request_sent = false;
            if(obj_this.active_chat_user.read || obj_this.is_request_sent){                    
                return;
            }
            obj_this.is_request_sent = true;
            let params = {
                target_id: obj_this.active_chat_user.id, 
                offset: obj_this.active_chat_user.messages.length
            };

            let args = {
                app: 'chat',
                model: 'message',
                method: 'get_old_messages'
            }
            let input_data = {
                params: params,
                args: args
            };
            let on_grouop_olde_messages = function(data){
                // console.log(params.offset, data);
                if(data.length > 0) {
                    obj_this.is_request_sent = false;
                    obj_this.update_emjoi_urls(data);

                    obj_this.active_chat_user.messages = obj_this.add_attachment(data,obj_this.active_chat_user.messages);
                    //do above

                    obj_this.scroll_to_end(".msg_card_body");
                    // $(".msg_card_body").scrollTop(100);
                }
                else
                {
                    obj_this.active_chat_user.read = true;
                }
            };
            input_data['no_loader'] = 1;
            obj_this.httpService.get(input_data, on_grouop_olde_messages, null);
        }
        //waiting because [data-emojiable=true] needs to render
        setTimeout(function(){
            var emoji_config = {
                emojiable_selector: "[data-emojiable=true]",
                assetsPath: "/static/assets/emoji/images",
                popupButtonClasses: "far fa-smile"
            };            
            var emojiPicker = new window["EmojiPicker"](emoji_config);
            emojiPicker.discover();
            
            if(already_fetched != 1)
            {
                obj_this.update_emjoi_urls(messages);		     
                obj_this.active_chat_user.messages =  obj_this.add_attachment(messages , null);
                //do above
            }
            
            obj_this.socketService.update_unseen_message_count(
                "user-selected",
                obj_this.active_chat_user
            );
            
            var emoji_editor = $('.emoji-wysiwyg-editor');            
            emoji_editor.unbind('keyup');            
            emoji_editor.keyup(function(e){                
				if(e.keyCode == 13 && !e.shiftKey)
				{
					obj_this.prepare_message();
				}
				$('.emoji-menu').hide();
            });

            $('#send_btn').unbind('click');
			$('#send_btn').click(function(){
				obj_this.prepare_message();
			});
            obj_this.scroll_to_end(".msg_card_body");	
        },20);
    }

	onUserSelected(messages: Array<Message>, already_fetched = 0) {        
        var obj_this = this;
        obj_this.message_offset = 0;
        obj_this.active_chat_user.read = false;        
        $( ".msg_card_body").unbind( "scroll" );
		$(".msg_card_body").scroll(function(){
            let scroll_top = $(".msg_card_body").scrollTop();
            if(!obj_this.active_chat_user)
            {
                console.log('Invalid chat user');
                return;
            }
            if(!obj_this.active_chat_user.messages)
            {
                // console.log('No chat user messages');
                obj_this.active_chat_user.messages = [];                
            }
			if(scroll_top < 2){
                get_user_old_messages();
			}
        });

        function get_user_old_messages(){
            if(obj_this.active_chat_user.messages.length < obj_this.message_limit)
            {
                return;
            }
            obj_this.is_request_sent = false;
            if(obj_this.active_chat_user.read || obj_this.is_request_sent){                    
                return;
            }

            obj_this.message_offset += obj_this.message_limit;
            obj_this.is_request_sent = true;
            let params = {
                target_id: obj_this.active_chat_user.id, 
                offset: obj_this.message_offset
            };

            let args = {
                app: 'chat',
                model: 'message',
                method: 'get_old_messages'
            }
            let input_data = {
                params: params,
                args: args
            };
            let on_user_old_message = function(data){
                // console.log(params.offset, data);
                if(data.length > 0) {
                    obj_this.is_request_sent = false;
                    obj_this.update_emjoi_urls(data);

                    obj_this.active_chat_user.messages = obj_this.add_attachment(data,obj_this.active_chat_user.messages);
                    //do above
                    obj_this.scroll_to_end(".msg_card_body");
                    // $(".msg_card_body").scrollTop(100);
                }
                else
                {
                    obj_this.active_chat_user.read = true;
                }
            };
            input_data['no_loader'] = 1;
            obj_this.httpService.get(input_data, on_user_old_message, null);
        }
        //waiting because [data-emojiable=true] needs to render
        setTimeout(function(){
            var emoji_config = {
                emojiable_selector: "[data-emojiable=true]",
                assetsPath: "/static/assets/emoji/images",
                popupButtonClasses: "far fa-smile"
            };            
            var emojiPicker = new window["EmojiPicker"](emoji_config);
            emojiPicker.discover();
            
            if(already_fetched != 1)
            {
                obj_this.update_emjoi_urls(messages);		     
                obj_this.active_chat_user.messages = obj_this.add_attachment(messages , null);
                ////do above with function
            }
            
            obj_this.socketService.update_unseen_message_count(
                "user-selected",
                obj_this.active_chat_user
            );
            
            var emoji_editor = $('.emoji-wysiwyg-editor');            
            emoji_editor.unbind('keyup');            
            emoji_editor.keyup(function(e){                
				if(e.keyCode == 13 && !e.shiftKey)
				{
					obj_this.prepare_message();
				}
				$('.emoji-menu').hide();
            });

            $('#send_btn').unbind('click');
			$('#send_btn').click(function(){
				obj_this.prepare_message();
			});
            obj_this.scroll_to_end(".msg_card_body");            
        },20);
	}

	send_message(input_data){   
        let obj_this = this;     
		try{
            let args = {
                app: 'chat',
                model: 'message',
                method: 'send',
            }
            if(input_data.attachments.length > 0)
            {
                args['post'] = 1;
            }
            if(obj_this.active_chat_user.is_group)
            {
                input_data.group_id = obj_this.active_chat_user.id;
                delete input_data['to'];
            }

            if(input_data.attachments.length)
            {
                setTimeout(function(){
                    window['js_utils'].addLoader($('.chat-message:last'), 'flex-end');
                }, 100);
            }
            
            input_data = {
                params: input_data,
                args: args,
                no_loader:1
            };           
			obj_this.httpService.post(input_data, function (data){
                // console.log(data);
                if(data.attachments.length)
                {
                    let messages = obj_this.active_chat_user.messages;
                    let len = obj_this.active_chat_user.messages.length;
                    var cnt = 0;
                    for(var i= len -1; i>=0; i--)
                    {
                        if(messages[i].uuid == data.uuid)
                        {                            
                            messages[i].attachments = data.attachments;
                            //do above with function
                            window['js_utils'].removeLoader($('.chat-message').eq(i));
                            // console.log(i, 1007);
                            break;
                        }
                        if(cnt++ > 4)
                        {
                            break;
                        }
                        // console.log(i, 5566);
                    }
                }
            }, null);
		}
		catch(er)
		{
			console.log(er, ' in sending message');
		}
    }
    
    file_change(event)
    {
        let obj_this = this;
        var res = new Promise<any>(function(resolve, reject) {
            window['functions'].get_file_binaries(event.target.files, resolve);
        }).then(function(data){            
            obj_this.attachments = obj_this.attachments.concat(data);
        });
    }
    
    attach_btn_click(ev)
    {
        if(!$(ev.target).is('input'))
        {
            $(ev.target).closest('.attach_btn').find('input').click();
        }        
    }
	prepare_message() {
        var obj_this = this;
        if(!obj_this.active_chat_user)
        {
            console.log('There must be some active user');
            return;
        }
        if(!obj_this.active_chat_user.messages)
        {
            console.log('Chat user must already have messages');
            obj_this.active_chat_user.messages = [];
        }

        var message_content = $('.emoji-wysiwyg-editor').html();
        if(message_content)
        {
            if(message_content.endsWith('<div><br></div>'))
            {
                message_content = message_content.slice(0, -15);
                if(message_content.endsWith('<div><br></div>'))
                {
                    message_content = message_content.slice(0, -15);
                }
            }
            if(message_content){
                message_content = message_content.replace(/^(\s*<br( \/)?>)*|(<br( \/)?>\s*)*$/gm, '');
            }
        }

        if (!message_content  && obj_this.attachments.length == 0){                
            $('.emoji-wysiwyg-editor').html('');
            return;
        }

        var date = new Date();
        var components = [
            date.getFullYear(),
            date.getMonth(),
            date.getDate(),
            date.getHours(),
            date.getMinutes(),
            date.getSeconds(),
            date.getMilliseconds()
        ];
        var timestamp = components.join("");        
        var input_data = {
            body: message_content,
            uuid : timestamp,
            attachments: obj_this.attachments,
			to: obj_this.active_chat_user.id,
            create_date: new Date(),
            no_loader: 1,
        };        
        obj_this.send_message(input_data);        
        if(message_content)
        {
            message_content = obj_this.sanitizer.bypassSecurityTrustHtml(message_content);
        }
        input_data.body = message_content;
        
        let temp = {
            id: null,
            from: obj_this.active_chat_user,
            body: message_content,
            create_date: Date(),
            sender: obj_this.user as BaseClient,
            attachments: obj_this.attachments,
            uuid: input_data.uuid
        };
        let obj_message = temp as Message;
        obj_this.add_message(obj_this.active_chat_user, obj_message);
        $('.emoji-wysiwyg-editor').html("");
        obj_this.attachments = [];
        $('form.attach_btn')[0].reset();
		obj_this.scroll_to_end(".msg_card_body");
    }    
    
	receiveMessage(message, sender_id: number) {   
        let obj_this = this;     
        let sender = obj_this.socketService.get_user_by_id(sender_id);
        if(!sender)
        {
            console.log(obj_this.socketService.chat_users, ' Dev issue as '+sender_id+' not found');
            return;
        }
        if(message.body)
        {
            message.body = obj_this.sanitizer.bypassSecurityTrustHtml(message.body);
        }
		var active_uid = parseInt($(".active_chat_user_id").html());
		var is_chat_open = $(".msg_card_body:visible").length >0 && active_uid == sender_id;
        
		if(!sender.messages)
		{
			sender.messages = [];
		}
        obj_this.add_message(sender, message);
        obj_this.socketService.update_unseen_message_count("receive-new-message", sender);
		if (is_chat_open) {
            let args = {
                app: 'chat',
                model: 'message',
                method: 'mark_read_message'
            }
            let input_data = {
                params: {message_id: message.id},
                args: args
            };
            input_data['no_loader'] = 1;
			obj_this.httpService.post(input_data, null, null);

            obj_this.socketService.update_unseen_message_count("read-new-message", sender);            
            setTimeout(function(){
                obj_this.scrollToEnd();
            }, 200)
		}
    }

    on_messge_from_new_group(group_id){
        let obj_this = this;
        let args = {
            app: 'chat',
            model: 'ChatGroup',
            method: 'get_details'
        }
        let input_data = {
            params: {group_id: group_id},
            args: args
        };
        input_data['no_loader'] = 1;        
        obj_this.httpService.post(input_data, function(data){
            obj_this.socketService.chat_groups.push(data);
        }, null);
    }

    receiveGroupMessage(message, sender_id: number) {    
        try{       
            let obj_this = this;
            if(message.sender.id == obj_this.user.id)
            {
                return;
            }
            if(!message.chat_group.id)
            {
                console.log('Invalid group id in message');
                return;
            }
            let temp = obj_this.socketService.chat_groups.filter(function(item){
                return item.id == message.chat_group.id;
            });
            if(temp.length == 0)
            {
                obj_this.on_messge_from_new_group(message.chat_group.id);
                return;
            }
            let group = temp[0];
            if(message.body)
            {
                message.body = obj_this.sanitizer.bypassSecurityTrustHtml(message.body);
            }
            
            var active_gid = undefined;
            if (obj_this.active_chat_user && obj_this.active_chat_user.is_group)
            {
                active_gid = obj_this.active_chat_user.id;
            }
            var is_chat_open = $(".msg_card_body:visible").length >0 && active_gid == message.chat_group.id;            
            if(!group.messages)
            {
                group.messages = [];
            }
            obj_this.add_message(group, message);
            obj_this.socketService.update_unseen_message_count("receive-new-message", group);
            if (is_chat_open) {
                let args = {
                    app: 'chat',
                    model: 'message',
                    method: 'mark_read_message'
                }
                let input_data = {
                    params: {message_id: message.id},
                    args: args
                };
                input_data['no_loader'] = 1;
                obj_this.httpService.post(input_data, null, null);
    
                obj_this.socketService.update_unseen_message_count("read-new-message", group);            
                setTimeout(function(){
                    obj_this.scrollToEnd();
                }, 200)
            }
        }
        catch(er){
            console.log(er);
        }
    }
    
    update_emjoi_urls(messages)
    {
        var obj_this = this;
        
        {
            messages.forEach(element => {
                if(element.body)
                {
                    element.body = obj_this.sanitizer.bypassSecurityTrustHtml(element.body);
                }
            });
        }
    }

    odoo_build = window['odoo'] ? 1 : undefined;
	is_mobile_device = false;
    ng_init = false;    

    remove_attachment(el){        
        let obj_this = this;                
        var i = $(el.target).closest('#attach_modal .doc-thumb').index();        
        obj_this.attachments.splice(i, 1);        
    }

    attachments = [];

    add_attachment(currentmessages=null, new_messages){
        var result;
        if(new_messages){
            if(new_messages.attachments){
                    // process_attachments(msg.attachments);  
            }
            result = currentmessages.concat(new_messages);
            // result = new_messages.concat(currentmessages);
        }else{
            result = currentmessages;
        }
        return result;
    }

	ngOnInit() {        
        var obj_this = this;
        obj_this.is_mobile_device = true;
        $('.popup.messenger').hide();

        if(!window['messenger-input'])
        {
            $(document).on('click', '.emoji-wysiwyg-editor', function(){                
                var target = obj_this.active_chat_user;
                if(target.unseen)
                {
                    obj_this.socketService.update_unseen_message_count ('user-selected', obj_this.active_chat_user);
                    let args = {
                        app: 'chat',
                        model: 'message',
                        method: 'get_friend_messages'
                    }
                    let input_data = {
                        params: {target_id: target.id},
                        no_loader:1,
                        args: args
                    };
                    obj_this.httpService.get(input_data, null, null); 
                }
                window['messenger-input'] = 1;
            })
        }
    }
}