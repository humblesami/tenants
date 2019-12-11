import { Component, OnInit, NgZone } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpService } from '../../app/http.service';
import { DomSanitizer } from '@angular/platform-browser';
import {SocketService} from "../../app/socket.service";
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { RosterComponent } from '../roster/roster.component';
import { TopiceditComponent } from '../topicedit/topicedit.component';
import { isArray } from 'util';

declare var $: any;

@Component({
	styleUrls:['./meetingdetails.css'],
	templateUrl: 'meetingdetails.component.html'
})

export class MeetingDetailsComponent implements OnInit {
	meeting_object: any;
    meetObjLoaded = false;
    token = '';
	notes = [];
	new_reply = '';
	next = '';
    prev = '';
    is_sortable_applied = false;
	title = '';
    flag = '';
    meeting_type = '';
    meeting_status = '';
	first_time = true;
    me_as_respondant: any;
    applicable_publish_action: string;
	discussion_params = {
		model:'Event',
		app:'meetings'
	}
    conference_not_active = false;
    socketService: SocketService;

	constructor(private route: ActivatedRoute,
				private router: Router,
				private httpService: HttpService,
				private sanitizer: DomSanitizer,
                private ss: SocketService,
                private zone: NgZone,
                private modalService: NgbModal) 
    {	

        this.socketService = this.ss;
        try
        {
            this.token = this.route.snapshot.params.token;
        }
        catch(e){
            this.token = '';
        }
        this.route.params.subscribe(params => this.get_data());
    }

    open_roster(){
        let obj_this = this;
		const modalRef = this.modalService.open(RosterComponent, { windowClass: 'roster-modal', keyboard: false,  backdrop: 'static' });
        modalRef.componentInstance.meeting_id = obj_this.meeting_object.id;
        modalRef.componentInstance.meeting_type = obj_this.meeting_object.exectime;
        modalRef.result.then(function(data){
            obj_this.meeting_object.attendance_marked = data && data.attendance_marked;
        });
    }

    delete_agenda_topic(evt, topic_id)
    {
        let obj_this = this;
        window['bootbox'].confirm('Are you sure to delete agenda item?', function(dr){
            if(dr){
                obj_this.delete_topic(evt, topic_id);
            }
        })
    }

    delete_topic(evt, topic_id){
        evt.stopPropagation();
        evt.preventDefault();
        let obj_this = this;
        if (!topic_id)
        {
            return;
        }
        let input_data = {
            topic_id: topic_id
        }
        let args = {
            app: 'meetings',
            model: 'Topic',
            method: 'delete_agenda_topic'
        }
        let final_input = {
            params: input_data,
            args: args
        }
        obj_this.httpService.get(final_input, (data)=>{
            obj_this.meeting_object.topics = data;            
        }, null)
    }

    add_edit_topic(evt, topic_id, action){        
        if(evt){
            evt.stopPropagation();
            evt.preventDefault();
        }
        let obj_this = this;
        var on_topic_closed = function(data){
            var temp_topics = []
            var pos = 0;
            for(var topic of obj_this.meeting_object.topics)
            {
                if(topic.position == undefined)
                {
                    topic.position = pos;
                }
                pos++;
                temp_topics.push(topic);
            }
            obj_this.zone.run(()=>{
                obj_this.meeting_object.topics = temp_topics;
            });
        };
        var fun = function(){
            // console.log(44343);
            const modalRef = obj_this.modalService.open(TopiceditComponent, { keyboard: false, backdrop: 'static' });
            modalRef.componentInstance.meeting_id = obj_this.meeting_object.id;
            modalRef.componentInstance.meeting_name = obj_this.meeting_object.name;
            modalRef.componentInstance.meeting_obj = 
            {
                "meeting_duration":obj_this.meeting_object.duration,
                "meeting_topics":obj_this.meeting_object.topics
            };
            modalRef.componentInstance.action = action;
            modalRef.componentInstance.topic_id = topic_id;
            modalRef.result.then(on_topic_closed);
        }
        fun();
    }

    open_topic_edit()
    {        
        let obj_this = this;
        if(obj_this.meeting_object.topics.length)
        {
            $('.router-outlet.meeting-details:first').scrollTop($("#agenda-items").offset().top - 130);
            return;
        }
		else{
            obj_this.add_edit_topic(null, null, 'create');
        }
    }

    on_publish_changed(e){
        let obj_this = this;
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'update_publish_status'
        }
        $(e.target).closest('button').attr('disabled', 'disabled');
        if(obj_this.meeting_status == 'Unpublished')
        {
            obj_this.meeting_status = 'Published';
        }
        else{
            obj_this.meeting_status = 'Unpublished';
        }
        let input_data = {
            params: {meeting_id: obj_this.meeting_object.id,publish_status: !obj_this.meeting_object.publish},
            args: args,
            no_loader: 1
        };
        obj_this.httpService.get(input_data, function(data){
            let is_published = obj_this.meeting_object.publish;
            $(e.target).closest('button').removeAttr('disabled');
            if (is_published)
            {
                obj_this.meeting_status = 'Unpublished';
                obj_this.applicable_publish_action = 'Publish';
                obj_this.meeting_type = 'draft';
                var elm = $('li.breadcrumb-item a').last();
                var parent_elm = elm.parent();
                elm.remove();
                parent_elm.append('<a href="#/meetings/draft">Draft Meetings</a>');
            }
            else
            {
                obj_this.meeting_status = 'Published';
                obj_this.applicable_publish_action = 'Unpublish';
                if(new Date(obj_this.meeting_object.end_date) > new Date())
                {
                    obj_this.meeting_type = 'upcoming';
                    var elm = $('li.breadcrumb-item a').last();
                    var parent_elm = elm.parent();
                    elm.remove();
                    parent_elm.append('<a href="#/meetings/upcoming">Upcoming Meetings</a>');
                }
                else{
                    obj_this.meeting_type = 'completed';
                    var elm = $('li.breadcrumb-item a').last();
                    var parent_elm = elm.parent();
                    elm.remove();
                    parent_elm.append('<a href="#/meetings/completed">Completed Meetings</a>');
                }
            }
            obj_this.meeting_object.publish = !is_published;
        }, function(){
            if (obj_this.meeting_object.publish)
            {
                $('.toggle_cb').prop('checked', true);                            
            }
            else
            {
                $('.toggle_cb').prop('checked', false);
            }
        });
    }

    is_attendee = false;
	get_data() {
        let obj_this = this;
		const page_url = window.location + '';
		let req_peram = (window.location + '').split('/');
		obj_this.flag = req_peram[req_peram.length - 3];
		if (['upcoming', 'completed', 'archived'].indexOf(obj_this.flag) === -1) {
			obj_this.flag = '';
		}
		
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'get_details'
        }
		let input_data = {
            params: {
                id: obj_this.route.snapshot.params.id, 
                meeting_type: obj_this.flag,
                token: obj_this.token,
            },
            args: args
        };

        let on_data = function(result) {
            // console.log(result,1122);
            if (obj_this.token)
            {
                window['functions'].get_public_feedback(result);
            }
            
            try {
                if(result.message)
                {
                    $('.router-outlet').html('<h2 style="text-align:center">'+result.message+'</h2>');
                    return;
                }
                var meeting_object = obj_this.meeting_object = result.meeting;                
                obj_this.next = result.next;
                obj_this.prev = result.prev;
                if (result.meeting && result.meeting.name) {
                } else {
                    obj_this.router.navigate(['/']);
                    return;
                }
                obj_this.meeting_type = result.meeting.exectime;
                obj_this.meeting_type === 'ongoing' ? obj_this.meeting_type = 'upcoming' : obj_this.meeting_type;
                if(obj_this.meeting_type)
                {
                    obj_this.meeting_type === 'past' ? obj_this.meeting_type = 'archived' : obj_this.meeting_type;
                    obj_this.title = obj_this.meeting_type[0].toUpperCase() + obj_this.meeting_type.slice(1).toLowerCase();
                }
                obj_this.meeting_object.description = obj_this.meeting_object.description.trim();                
                if(meeting_object.description)
                    meeting_object.description = obj_this.sanitizer.bypassSecurityTrustHtml(obj_this.meeting_object.description);
                var uid = window['current_user'].cookie.id;

                var pp = 0
                var cur_user_object = undefined;
                var myindex = -1;
                var attendees = meeting_object.attendees;
                if (attendees)
                {
                    attendees.forEach(att => {
                        if (att.uid == uid) {
                            myindex = pp;
                            cur_user_object = att;
                        }
                        pp++;
                    });
                    if(!cur_user_object)
                    {
                        obj_this.is_attendee = false;
                    }
                    else{
                        obj_this.is_attendee = true;
                    }
                    attendees.splice(myindex, 1);
                    attendees.splice(0, 0, cur_user_object);
                    obj_this.me_as_respondant = attendees[0];
                }
                if (obj_this.meeting_object.publish)
                {
                    obj_this.meeting_status = 'Published';
                    obj_this.applicable_publish_action = 'Unpublish';
                }
                else
                {
                    obj_this.meeting_status = 'Unpublished';
                    obj_this.applicable_publish_action = 'Publish';
                }
                if (meeting_object.surveys)
                {
                    for(var survey of meeting_object.surveys)
                    {
                        survey.open_date = window['dt_functions'].meeting_time(survey.open_date);
                    }
                }
                if (meeting_object.votings)
                {
                    for(var voting of meeting_object.votings)
                    {
                        voting.open_date = window['dt_functions'].meeting_time(voting.open_date);
                    }
                }

                setTimeout(function(){
                    if (obj_this.meeting_object.publish)
                    {
                        $('.toggle_cb').prop('checked', true);                            
                    }
                    else
                    {
                        $('.toggle_cb').prop('checked', false);
                    }
                    if (obj_this.socketService.admin_mode && $('#agenda_tbody').length)
                    {
                        $('#agenda_tbody').sortable({
                            stop: function (event, ui) {
                                obj_this.save_positions();
                            },
                        });
                    }
                }, 100);
                // console.log(meeting_object, obj_this.token, 333);
            } catch (er) {
                console.log(er);
            }
            obj_this.meetObjLoaded = true;
        };
        if (!obj_this.token)
        {
            this.httpService.get(input_data, on_data, null);
        }
        else
        {
            obj_this.httpService.post_public(input_data, on_data, (result)=>{
                window['functions'].get_public_feedback(result);
            });
        }
    }

    save_positions(evn = undefined, dir = undefined){
        let obj_this = this;
        var data = [];        
        if(evn){
            var tr = undefined;
            var tbody = undefined;
            tr = $(evn.target).closest('tr');
            tbody = tr.closest('tbody');
            // console.log(tr[0]);
            if(dir == 'down'){     
                var next = tr.next();
                next.after(tr);
            }
            if(dir == 'up'){
                var prev = tr.prev();
                prev.before(tr);
            }            
        }

        var temp_topics = [];
        $('#agenda_tbody tr').each(function(i, el){
            data.push({
                id:$(el).find('input.id:first').val(),
                position: i
            });            
            var topic = obj_this.meeting_object.topics.find(function(item){
                return item.id == data[i].id;
            });
            topic.position = i;
            temp_topics.push(topic);
        });
        obj_this.zone.run(()=>{
            obj_this.meeting_object.topics = temp_topics;
        });
        
        
        obj_this.httpService.get({
            params:{
                topics: data,
            },
            args:{
                app: 'meetings',
                model:'Topic',
                method:'update_positions'
            },
        }, function(){
            
        }, null);
    } 

    move_to_archive(meeting_id:number)
    {
        // console.log(43);
        let obj_this = this;
        if (meeting_id)
        {
            let args = {
                app: 'meetings',
                model: 'Event',
                method: 'move_to_archive'
            }
            let input_data = {
                params: {meeting_id: meeting_id},
                args: args,
                no_loader: 1
            };            
            if (obj_this.meeting_object.attendance_marked)
            {                
                obj_this.httpService.get(input_data, function(data){
                    var url = '/meeting/archived/' + meeting_id
                    obj_this.router.navigate([url]);
                }, null)
            }
            else{
                window['bootbox'].alert('Please click Roster to mark all attendance first');
            }
        }
    }
    attachments = [];


    doc_name_change(doc, e)
    {
        doc.name = e.target.value;
    }


    file_change(event)
    {
        let obj_this = this;
        var res = new Promise<any>(function(resolve, reject) {
            window['functions'].get_file_binaries(event.target.files, resolve);
        }).then(function(data){
            data.forEach(element => {
                let ar = element.name.split('.')
                element.ext = ar[ar.length - 1];
                element.name = element.name.replace('.' + element.ext, '');
                element.file_name = element.name;
            });
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


    remove_attachment(el){        
        let obj_this = this;                
        var i = $(el.target).closest('#attach_modal .doc-thumb').index();        
        obj_this.attachments.splice(i, 1);        
    }


    upload_doucments()
    {
        var obj_this = this;
        obj_this.attachments.forEach(element =>{
            element.file_name = element.name;
            element.name = element.name + '.' + element.ext;
        });

        if (obj_this.attachments.length && obj_this.meeting_object)
        {
            let args = {
                app: 'meetings',
                model: 'MeetingDocument',
                method: 'upload_meeting_documents',
                post: 1
            }
            let input_data = {
                params: {
                    meeting_id: obj_this.meeting_object.id,
                    attachments: obj_this.attachments
                },
                args: args,
                no_loader: 1
            };
            obj_this.httpService.get(input_data, function(data){
                obj_this.meeting_object.meeting_docs = obj_this.meeting_object.meeting_docs.concat(data);
                obj_this.attachments = []
            }, null);
        }
    }
    visible_limit = {
        survey : 1,
        sign_doc : 1,
        news_doc : 1,
        news_video: 1,
        voting: 1,
    };
    ng_init = false;
    start_indices = {
        survey : 0,
        sign_doc : 0,
        news_doc : 0,
        news_video: 0,
        voting: 0,
    };
    ending_indices = {
        survey : 0,
        sign_doc : 0,
        news_doc : 0,
        news_video: 0,
        voting: 0,
    }

    update_indices(){

    }
    get_slider_start_index(flag, items, item_type){
        
        if(!items)
        {
            return;
        }
        if(this.start_indices[item_type] + flag * this.visible_limit[item_type] >= items.length)
        {
            this.start_indices[item_type] = 0;
        }
        else if(this.start_indices[item_type] + flag * this.visible_limit[item_type] < 0)
        {
            this.start_indices[item_type] = items.length % this.visible_limit[item_type] > 0 ? items.length - items.length % this.visible_limit[item_type] : items.length - this.visible_limit[item_type];
        }
        else
        {
            this.start_indices[item_type] += flag * this.visible_limit[item_type];
        }
        this.ending_indices[item_type] =  this.start_indices[item_type] + this.visible_limit[item_type];
        // console.log(this.visible_limit[item_type],this.start_indices[item_type],items,item_type);
    }

    on_admin_mode_changed()
    {
        let obj_this = this;
        if (this.socketService.admin_mode)
        {
            obj_this.is_sortable_applied = true;
            if($('#agenda_tbody').length)
            {
                    $('#agenda_tbody').sortable({
                    stop: function (event, ui) {
                        obj_this.save_positions();
                    },
                });
            }
        }
        else
        {
            if(obj_this.is_sortable_applied)
            {
                if($('#agenda_tbody').length)
                {
                    $('#agenda_tbody').sortable('destroy');
                }
            }
        }
    }

	ngOnInit() {
        let obj_this = this;
        var vw = $(window).width();        
        if(vw > 1200)
        obj_this.visible_limit = {
            survey : 3,
            sign_doc : 6,
            news_doc : 6,
            news_video: 4,
            voting: 3,
        }
        else if(vw > 991 && vw < 1200)
        obj_this.visible_limit = {
            survey : 3,
            sign_doc : 4,
            news_doc : 6,
            news_video: 4,
            voting: 3,
        }
        else if(vw > 767 && vw < 992)
        obj_this.visible_limit = {
            survey : 2,
            sign_doc : 3,
            news_doc : 3,
            news_video: 3,
            voting: 2,
        }
        else if(vw > 576 && vw < 768)
        obj_this.visible_limit = {
            survey : 1,
            sign_doc : 2,
            news_doc : 2,
            news_video: 2,
            voting: 1,
        }
        else
        obj_this.visible_limit = {
                survey : 1,
                sign_doc : 1,
                news_doc : 1,
                news_video: 1,
                voting: 1,
            };

        for (var item_type in obj_this.ending_indices)
        {
            obj_this.ending_indices[item_type] = obj_this.visible_limit[item_type];
        }

        obj_this.socketService.call_backs_on_mode_changed['handle_sortable'] = function(){
            obj_this.on_admin_mode_changed();
        };
        // console.log(obj_this.visible_limit, obj_this.ending_indices,1122);
	}

	ngOnDestroy() {

	}
}
