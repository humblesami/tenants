import { Component, OnInit, Input } from '@angular/core';
import {HttpService} from "../../app/http.service";
import {SocketService} from "../../app/socket.service";
import {ActivatedRoute} from "@angular/router";
declare var $: any;


@Component({
	selector: 'app-comments',
	styleUrls:['./comments.css'],
	templateUrl: './comments.component.html'	
})
export class CommentsComponent implements OnInit {

    @Input() res_app: string;
    @Input() res_model: string;
    @Input() res_id: string;
    @Input() mention_list: any;

	comments = [];
	notes = [];
	new_reply = '';
	comment_subtype = undefined;
    new_comment = '';
    active_comment : any;
    mentionConfig: any;
    // mentionedList: any;
    post_btn_disable: boolean;
    should_save: boolean;
	constructor(private httpService: HttpService,
				private socketService: SocketService,
				private route: ActivatedRoute) {
                    // this.mentionedList = []
                    this.should_save = true;
                    if(!this.mention_list)
                    {
                        this.mention_list = [];
                        console.log('No mention list given');
                    }
                }

	get_data(input_data) {
        var obj_this = this;
        
        let on_comments_list = function(result){
            try {
                obj_this.comment_subtype = 1;
                var read_notification_ids = result.read_notification_ids;                
                result = result.comments;
                for(let i in result) {
                    var item = result[i];
                    if (item.subtype_id) {
                        if (item.subtype_id === 1) {
                            item.reply = false;
                            if(item.body && item.body.startsWith('<p>'))
                            {                                
                                item.body = $(item.body)[0].innerHTML;
                            }
                            obj_this.add_item(item, obj_this.comments, 'read comment', 0);
                        } else if (item.subtype_id === 2) {
                            if(item.body && item.body.startsWith('<p>'))
                            {
                                item.body = $(item.body)[0].innerHTML;
                            }
                            obj_this.add_item(item, obj_this.notes, 'read note', 0);
                        }
                    }
                    if(item.children)
                    {
                        for(let j in item.children) {
                            var child_item = item.children[j];
                            if(child_item.body && child_item.body.startsWith('<p>'))
                            {                                
                                child_item.body = $(child_item.body)[0].innerHTML;
                            }
                        }
                    }
                    
                    //item.showRep = true;
                }
            }
            catch (er) {
                console.log(er);
            }
        }
        let args = {
            app: 'chat',
            model:'Comment',
            method:'get_comments',
        }
        input_data = {
            params: input_data,
            args: args
        }
		this.httpService.get(input_data, on_comments_list,null);
    }
    
    add_item(item, collection, add_type, at_start){
        if(!item.user)
        {
            console.log('Bad item in '+add_type);            
            return;
        }
        else
        {
            // console.log(item.user);
            if(at_start == 1)
            {
                collection.splice(0, 0, item);
            }
            else{
                collection.push(item);
            }
            
        }
    }

	showReplies(evt, com) {
        // evt.preventDefault();
        com['showRep'] = !com['showRep'];
        if(com.children.length>5){
            return
        }
        if(!com['showRep']){
            var doc_height = $('.comments.comments-container').height();
            // console.log(doc_height, 333);
            setTimeout(function(){
                $('.comments.comments-container').height(doc_height);
                doc_height = $('.comments.comments-container').height();
            }, 10);
            
        }
	}

    manage_comment()
    {
        $('.mention-div-reply').removeClass('active-mention');
        $('.mention-div-comment').addClass('active-mention');
    }
    manage_reply_class()
    {
        $('.mention-div-comment').removeClass('active-mention');
        $('.mention-div-reply').addClass('active-mention');
    }

	commentReply(evt, comment) {
        this.new_reply = '';        
        if(this.active_comment)
            this.active_comment.active = false;
        comment.active = true;
        let mention_reply = $('.mention-div-reply:first');
        $(evt.target).closest('.CommentWrapper').append(mention_reply);
        mention_reply.show();
        comment['showRep'] = true;
        this.active_comment = comment;
        //evt.preventDefault(); does not work
        setTimeout(function(){                        
            $('.reply-box:first').focus();
            $('.mention-div-reply').addClass('active-mention');
        }, 100);
        $('.mention-div-comment').removeClass('active-mention');        
    }

    save_comment_key_up(e, parent){
        let obj_this = this;
        // if (e.currentTarget.textContent.length)
        // {
        //     obj_this.post_btn_disable = true;
        // }
        
        if (obj_this.should_save)
        {
            if(e.keyCode == 13 && !e.shiftKey){
                e.preventDefault();
                if(parent == 'reply')
                {
                    // console.log(e.target, $(e.target).prev()[0]);
                    let cid = $(e.target).closest('.CommentWrapper').find('input.comment_id').val()
                    parent = obj_this.comments.find(function(item){
                        return item.id == cid;
                    });
                    console.log(e.target,parent);
                    // console.log(cid, parent);
                }
                obj_this.save_comment(parent);
            }
        }
        else
        {
            obj_this.should_save = true;
        }
    }
    
	save_comment(parent_item)
	{
        let mention_list = []
        $('.active-mention a.mention').each(function(i, el){
            let mentioned_id = $(el).attr('mentioned_id');
            if(mention_list.indexOf(mentioned_id) == -1)
            {
                mention_list.push(parseInt(mentioned_id));
            }
        });

        let obj_this = this;
        obj_this.new_comment = $('.active-mention').html().replace('<div><br></div>', '');        
        obj_this.new_reply = obj_this.new_comment;
        obj_this.post_btn_disable = false;
		let item = {
			res_model: obj_this.res_model,
            res_id: obj_this.res_id,
            res_app: obj_this.res_app,
			subtype_id: obj_this.comment_subtype,
			create_date : new Date(),
            user: obj_this.socketService.user_data,
            mentioned_list: mention_list,
            user_id:  obj_this.socketService.user_data.id
        };
        if(item.subtype_id == 2)
        {
            item['body'] = obj_this.new_comment;
            if(!item['body'] && ! mention_list.length)
            {
                return;
            }
            obj_this.add_item(item, obj_this.notes, 'created note', 1);
			this.new_comment = '';
        }
        else
        {
            if(parent_item)
            {
                item['parent_id'] = parent_item.id;
                item['body'] = obj_this.new_reply;
                if(!item['body'] && ! mention_list.length)
                {
                    return;
                }
                if(!Array.isArray(parent_item.children))
                    parent_item.children = [item]
                else
                {
                    obj_this.add_item(item, parent_item.children, 'cr reply', 0);
                }                
                item['reply'] = 1;
            }
            else
            {
                item['body'] = obj_this.new_comment;
                if(!item['body'] && ! mention_list.length)
                {
                    return;
                }
                obj_this.add_item(item, obj_this.comments, 'created comment', 1);                
                item['reply'] = false;
            }                                    
        }        
        this.new_reply = '';
        this.new_comment = '';
        $('.active-mention').html('');
        // console.log(obj_this.comments);
        let input_data = {
            args: {
                app: 'chat',
                model: 'Comment',
                method: 'add'
            },
            no_loader: 1,
            params: item
        }
		this.httpService.post(input_data, function(data){
            item['id'] = data.id;
        }, null);
	}

	deleteComment(id, type) {
        let obj_this = this;
        
        let args = {
            app: 'chat',
            model: 'message',
            method: 'unlink'
        }
		let input_data = {
            params: {id: id},
            args: args
        };

        let on_deleted = function(result: any) {
            if (type === 'comment') {
                for (let i = 0; i < obj_this.comments.length; i++) {
                    if (obj_this.comments[i].id === id) {
                        obj_this.comments.splice(i, 1);
                        break;
                    }
                }
            } else if (type === 'note') {

                for (let i = 0; i < obj_this.notes.length; i++) {
                    if (obj_this.notes[i].id === id) {
                        obj_this.notes.splice(i, 1);
                        break;
                    }
                }
            }
            else {
                for (let i = 0; i < obj_this.comments.length; i++) {
                    if (obj_this.comments[i].id === type) {
                        var replies = obj_this.comments[i].children;
                        for (let j = 0; j < replies.length; j++)
                        {
                            if(replies[j].id == id)
                                replies.splice(j, 1);
                        }
                        break;
                    }
                }
            }			
        }
		obj_this.httpService.post(input_data,on_deleted, null);
	}

	cancelComment() {
		this.new_comment = '';
    }

    comment_reply_keydown(e){
        if(e.keyCode == 13 && !e.shiftKey)
        {
            e.preventDefault();
        }
    }
    
	ngOnInit() {
        let obj_this = this;
        let me_id = obj_this.socketService.user_data.id;
        obj_this.mention_list = obj_this.mention_list.filter(function(obj){
            return obj.id != me_id;
        });

        if (obj_this.mention_list)
        {
            obj_this.mentionConfig = {
                items: obj_this.mention_list,
                insertHTML: true,
                triggerChar: "@",
                dropUp: true,
                labelKey: 'name',
                mentionSelect: function(val){
                    obj_this.should_save = false;
                    let el = $('.active-mention');
                    let tag = $('<a class="mention" mentioned_id="'+val.id+'" href="/#/'+val.group+'/'+val.id+'">'+val.name+'</a>');
                    el.append(tag);
                    let inputValue = el.html();
                    let secondString = inputValue.substring(inputValue.lastIndexOf('@'), inputValue.length-1);
                    let replaceValue = secondString.substring(0, secondString.indexOf('<'));
                    el.html(el.html().replace(replaceValue, ''));
                    obj_this.placeCursorAtEnd();
                    return '';
                }
            };
        }
		let input_data = {
			res_model: obj_this.res_model,
            res_id: obj_this.res_id,
            res_app: obj_this.res_app,
            subtype_id : obj_this.comment_subtype,
			no_loader: 1
        };
        obj_this.get_data(input_data);
        // console.log(3232);
        obj_this.socketService.server_events['comment_received'] = function (data) {
            // console.log(data, 76);
			var container = $('.comments.main-container');
			if(container.length < 1)
			{
				return;
            }
            
            if (obj_this.res_app != data.res_app || obj_this.res_id != data.res_id || obj_this.res_model != data.res_model) {
                return;
            }
            if (data.parent_id) {
                for (var i in obj_this.comments) {
                    if (obj_this.comments[i].id == data.parent_id) {
                        obj_this.add_item(data, obj_this.comments[i].children, 'rec reply', 0);
                        break;
                    }
                }
            }
            else {
                obj_this.add_item(data, obj_this.comments, 'rec comment', 1);
            }
        };
    }

    placeCursorAtEnd() {
        let contentEditableElement = $('.active-mention')[0];
        var range,selection;
        if(document.createRange)//Firefox, Chrome, Opera, Safari, IE 9+
        {
            range = document.createRange();//Create a range (a range is a like the selection but invisible)
            range.selectNodeContents(contentEditableElement);//Select the entire contents of the element with the range
            range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
            selection = window.getSelection();//get the selection object (allows you to change selection)
            selection.removeAllRanges();//remove any selections already made
            selection.addRange(range);//make the range you have just created the visible selection
        }
    }
        
}
