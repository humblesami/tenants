import { isArray } from 'util';
import { Component, OnInit, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { HttpService } from '../../app/http.service';
import {SocketService} from "../../app/socket.service";
import { RenameService } from 'src/app/rename.service';
import { Router } from '@angular/router';
// import { toInteger } from '@ng-bootstrap/ng-bootstrap/util/util';

declare var $: any;
@Component({
    selector: 'app-topicedit',
    templateUrl: './topicedit.component.html',
    styleUrls: ['../profileedit/profileedit.component.css',
    '../documents/documents.component.css','./topicedit.component.css'
    ]
})
export class TopiceditComponent implements OnInit {
    @Input() meeting_id: any;
    @Input() meeting_name: any;
    @Input() action: any;
    @Input() meeting_obj: any;
    @Input() new_topic_valid_time:any;
    @Input() topic_id: any;
    socketService: SocketService;
    renameService: RenameService;
    modified_topic_data = {
        name: '',
        description: '',
        lead: '',
        duration: ''
    };
    agenda_docs = [];
    event__name = '';
    add_another = false;
    added_topics = [];
    topic = {
        name: '',
        description: '',
        lead: '',
        duration: '',
        docs: []
    };
    constructor(
        public activeModal: NgbActiveModal,
        private httpService: HttpService,
        private renameSer: RenameService,
        private ss: SocketService,
        public router: Router
    ) {
        this.socketService = ss;
        this.renameService = renameSer;
    }

    onAddAnother() {
        this.add_another = true;
        this.onSubmit();
    }

    onCancel() {        
        this.activeModal.close('closed');        
    }

    get_icon_url(source = null) {
        var icon_url = "/static/assets/images/cloud/local.png";
        switch (source) {
            case "Google":
                icon_url = "/static/assets/images/cloud/gdrive.png";
                break;
            case "Onedrive":
                icon_url = "/static/assets/images/cloud/onedrive.png";
                break;
            case "Dropbox":
                icon_url = "/static/assets/images/cloud/dropbox.png";
                break;
        }
        return icon_url;
    }

    clear_form() {
        let obj_this = this;
        if (obj_this.action == 'update') {
            obj_this.action = 'create';
            setTimeout(() => {
                obj_this.apply_drag_drop();
            }, 10);
        }
        obj_this.add_another = false;
        
        obj_this.topic = {
            name: '',
            description: '',
            lead: '',
            docs: [],
            duration: ''
        };
        obj_this.modified_topic_data = {
            name: '',
            description: '',
            lead: '',
            duration: ''
        };
        obj_this.agenda_docs = [];
        // console.log(32323, 5788);
        $('#duration').val('0').trigger('change');
    }

    delete_file(evn, doc_id) {
        evn.stopPropagation();
        evn.preventDefault();
        let obj_this = this;
        window['bootbox'].confirm('Are you sure to delete?', function(dr) {
            if (!dr) {
                return;
            }
            let input_data = {
                doc_id: doc_id,
            }
            let args = {
                app: 'documents',
                model: 'File',
                method: 'delete_file'
            }
            let final_input = {
                params: input_data,
                args: args
            }

            obj_this.agenda_docs.find((item) => {
                return item.id == doc_id;
            }).deleting = true;

            obj_this.httpService.get(final_input, (data) => {
                obj_this.agenda_docs = obj_this.agenda_docs.filter((el) => {
                    return doc_id != el.id;
                });
            }, null);
        });
    }

    dur_focus(evn){
        let obj_this = this;
        obj_this.modified_topic_data.lead = evn;
        $("#foo_dur").click();        
        setTimeout(function(){
            $("#dur_hours").focus();
        }, 100);
    }    
    onSubmit() {        
        let obj_this = this;
        if(obj_this.time_exceeded || !(obj_this.topic.name && obj_this.topic.lead && obj_this.topic.duration))
        {
            return;
        }
        // console.log(obj_this.modified_topic_data.duration, 3444);
        if(!obj_this.modified_topic_data.duration)
        {
            obj_this.modified_topic_data.duration = obj_this.topic.duration;            
        }

        const form_data = obj_this.modified_topic_data;
        const input_data = {};
        for (const key in form_data) {
            if (obj_this.modified_topic_data[key] != '')
            {
                input_data[key] = obj_this.modified_topic_data[key];
            }
        }
        let args = {
            app: 'meetings',
            model: 'Topic',
            post: 1,
        }
        if (obj_this.action == 'update') {
            input_data['topic_id'] = obj_this.topic_id;
            args['method'] = 'update_agenda_topic';
        } else {
            args['method'] = 'save_agenda_topic';
            if (obj_this.meeting_id) {
                input_data['meeting_id'] = obj_this.meeting_id;
            }
        }
        input_data['agenda_docs'] = obj_this.agenda_docs;
        let final_input_data = {
            params: input_data,
            args: args
        }
        obj_this.httpService.get(final_input_data, (data) => {
            // console.log(data, obj_this.topic_id, 3444);
            if (obj_this.topic_id) {                
                var topic = obj_this.meeting_obj.meeting_topics.find((el, i)=>{                        
                    return el.id == obj_this.topic_id;
                });
                let index = obj_this.meeting_obj.meeting_topics.indexOf(topic);
                obj_this.meeting_obj.meeting_topics[index] = data;
            }
            else{
                obj_this.meeting_obj.meeting_topics.push(data);                
            }

            if (!obj_this.add_another) {                
                obj_this.activeModal.close('saved');
            } else {
                obj_this.clear_form();
                data = obj_this.added_topics
                obj_this.submitted = false;
                obj_this.topic_id = '';
                obj_this.sum_agenda_duration(null);
            }
        }, null);
    }

    duration_to_number(duration){
        if(duration){
            duration = duration.split(":")
            let duration_hours = parseInt(duration[0]);
            let duration_minuets = parseInt(duration[1]);
            if(duration_hours>0){
                    duration_hours = duration_hours * 60 * 60;
                }
            if(duration_minuets> 0){
                duration_minuets = duration_minuets * 60;
            }
            duration = duration_hours + duration_minuets;
            return duration;
        }
    }
    time_exceeded = false;
    submitted = false;
    available_duration= undefined;
    sum_agenda_duration(evn){
        let obj_this = this;
        // console.log(obj_this.topic.duration,2322323232323);
        obj_this.time_exceeded = false;
        var other_topics_duration = 0;
        var topics = obj_this.meeting_obj.meeting_topics
        for(var topic of topics)
        {
            var num =  parseInt(topic.duration)
            
            if(topic.id != obj_this.topic_id)
            {
                other_topics_duration += num;
            }
        }
        var meeting_duration_seconds = obj_this.duration_to_number(obj_this.meeting_obj.meeting_duration);
        // console.log(meeting_duration_minuets, 444);
        let available_time = meeting_duration_seconds - other_topics_duration;
        if(meeting_duration_seconds >= other_topics_duration){            
            // var available_time_string = obj_this.timeConvert(available_time);            
            if(evn){
                var picker_duration = $("#duration");
                var new_topic_duration = picker_duration.val();
                
                if( available_time < new_topic_duration || new_topic_duration == 0){                    
                    obj_this.time_exceeded = true;
                    obj_this.available_duration = window['dt_functions'].seconds_to_hour_minutes(available_time);
                }else{
                    var remian = window['dt_functions'].seconds_to_hour_minutes(available_time - new_topic_duration );
                    obj_this.available_duration = remian;
                    obj_this.modified_topic_data.duration =  new_topic_duration;
                    obj_this.topic.duration = new_topic_duration;
                }
            }else{
                setTimeout(()=>{
                    obj_this.available_duration = window['dt_functions'].seconds_to_hour_minutes(available_time);
                    var picker_duration = $("#duration");
                    picker_duration.value = available_time;
                    // obj_this.modified_topic_data.duration = available_time ;
                },10);
            }
        }else{
            obj_this.time_exceeded = true;
            obj_this.available_duration = window['dt_functions'].seconds_to_hour_minutes(available_time);
        }
    }

    get_topic() {
        let obj_this = this;
        const input_data = {
            id: obj_this.topic_id
        };
        let args = {
            app: 'meetings',
            model: 'Topic',
            method: 'get_details'
        }

        let final_input_data = {
            params: input_data,
            args: args
        };
        obj_this.httpService.get(final_input_data, (data) => {
            obj_this.topic = data;
            setTimeout(function(){                
                $('#duration').trigger('change');
            }, 10)
            
            obj_this.event__name = data.event__name;
            if (obj_this.topic.docs.length) {                
                obj_this.agenda_docs = obj_this.topic.docs;
            }
        }, null);
    }

    redirect_to_doc(link) {
        this.activeModal.close();
        this.router.navigate([link]);
    }

    apply_drag_drop() {
        let obj_this = this;
        let file_input = $('.add_agenda_docs');
        let resInfo = {
            res_app: 'documents',
            res_model: 'File'
        }
        file_input.attr('dragdrop', 1);
        window['apply_drag_drop'](file_input, resInfo, function(data) {
            try {
                for (let doc of data) {
                    obj_this.agenda_docs.push(doc);
                }
            } catch (er) {
                console.log(er, 5455);
            }
        });
    }


    ngOnInit() {
        let obj_this = this;
        if (obj_this.meeting_name) {
            obj_this.event__name = obj_this.meeting_name;
        }
        if (obj_this.action == 'update' && obj_this.topic_id) {            
            obj_this.get_topic()
        }
        
        window['app_libs']['duration_picker'].load(function(){            
            $('#duration').durationPicker({showSeconds: false,showDays: false});
        });

        // else if(obj_this.action == 'create')
        {
            setTimeout(() => {
                obj_this.apply_drag_drop();
            }, 10);
        }
        // console.log(obj_this.meeting_obj);
        obj_this.sum_agenda_duration(null);
        
        $(document).ready(function() {
            var $timerVal = $("#duration");
            $timerVal.on('change',function() {
                // console.log(677878);
                var duration_second = $timerVal.val();
                if(duration_second){
                    obj_this.sum_agenda_duration(duration_second);
                }else{
                    duration_second = $timerVal.value = 0
                    obj_this.sum_agenda_duration(duration_second);
                }
            });                    
        });
    }

}