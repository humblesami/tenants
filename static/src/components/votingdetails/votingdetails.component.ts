import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpService } from '../../app/http.service';
import {SocketService} from "../../app/socket.service";
declare var $: any;

@Component({
    selector: 'app-votingdetails',
    styleUrls:['./meetingdetails.css', './votingdetails.css'],
    templateUrl: './votingdetails.component.html'
})
export class VotingdetailsComponent implements OnInit {    
    voting_object: any;
    notes = [];
    new_reply = '';
    bread_crumb = {
        items: [],
        title: ''
    };
    discussion_params = {
        res_app: 'voting',
        res_model: 'Voting',
        res_id: 0,
    }
    next = '';
    prev = '';
    title = '';
    flag = '';
    first_time = true;
    me: any;
    Chart: any;
    conference_not_active = false;
    chart_data: any;
    token = '';
    constructor(private route: ActivatedRoute,
                private router: Router,
                private httpService: HttpService,
                private socketService: SocketService) {
        try
        {
            this.token = this.route.snapshot.params.token;
        }
        catch(e){
            this.token = '';
        }
        this.route.params.subscribe(params => this.get_data());
    }

    get_data() {
        this.bread_crumb = {
            items: [],
            title: ''
        };
        const page_url = window.location + '';
        let req_peram = (window.location + '').split('/');
        this.flag = req_peram[req_peram.length - 3];
        if (['upcoming', 'completed', 'archived'].indexOf(this.flag) === -1) {
            this.flag = '';
        }
        
        const obj_this = this;
        const input_data = {
            id: this.route.snapshot.params.id,
            token: obj_this.token
        };
        let on_data = function(result) {
            if (obj_this.token && result == 'done')
            {
                window['functions'].get_public_feedback(result);
            }
            try {               
                if(result.message)
                {
                    $('.router-outlet').html('<h2 style="text-align:center">'+result.message+'</h2>');
                    return;
                }
                obj_this.discussion_params.res_id = result.id;
                if(!result.results)
                {
                    result.results = {};
                }
                obj_this.voting_object = result;
                
                if(obj_this.socketService.admin_mode || 
                    (obj_this.voting_object.chart_data.length && 
                        obj_this.voting_object.public_visibility))
                {
                    setTimeout(function(){
                        var chart_colors = window['chart_colors'];
                        var p =0;
                        let question = obj_this.voting_object;
                        for(let j in question.chart_data){
                            if(p>=chart_colors.length)
                            {
                                p = 0;
                            }
                            question.chart_data[j].color = chart_colors[p++];
                        }

                        if(obj_this.voting_object.results.answer_count)
                        {
                            window['app_libs']['chart'].load(()=>{
                                window['drawChart'](obj_this.voting_object.chart_data, '#myChart');
                            });
                        }
                        if(obj_this.voting_object.progress_data)
                        {
                            window['app_libs']['chart'].load(()=>{
                                window['drawChart'](obj_this.voting_object.progress_data, '#progress-chart');
                            });
                        }
                    }, 100)
                }                
                
            } catch (er) {
                console.log(er);
            }           
        };
        let args = {
            app: 'voting',
            model: 'Voting',
            method: 'get_details'
        }           
        let final_input_data = {
            params: input_data,
            args: args
        };
        if (!obj_this.token)
        {
            obj_this.httpService.get(final_input_data, on_data, null);
        }
        else
        {
            obj_this.httpService.post_public(final_input_data, on_data, (result)=>{
                window['functions'].get_public_feedback(result);
            });
        }
        function make_bread_crumb(page_title) {
            const bread_crumb_items = obj_this.bread_crumb.items;
            if(obj_this.voting_object.topic.name)
            {
                bread_crumb_items.push({title: obj_this.voting_object.topic.name, link: '/topic/'+obj_this.voting_object.topic.id});
            }
            else if(obj_this.voting_object.meeting.name)
            {
                bread_crumb_items.push({title: obj_this.voting_object.meeting.name, link: '/home/meeting/'+obj_this.voting_object.meeting.id});
            }
            if (page_title) {
                obj_this.bread_crumb.title = page_title;
            }
        }
    }
    
    voting_closed(close_date: string){
        let closed = false;
        let closingDate = new Date(close_date).getTime();
        let dateNow = new Date().getTime();
        if (closingDate < dateNow){
            closed = true;
        }
        return closed;
    }

    voting_opened(open_date: string){
        let opened = false;
        let openingDate = new Date(open_date).getTime();
        let dateNow = new Date().getTime();
        if (openingDate > dateNow){
            opened = true;
        }
        return opened;
    }

    respond_invitation(option_name: string, response: number, voting_id: number) {
        let obj_this = this;
        let chek = $('.upcomingButton .fa-check:first');
        if(chek.length > 0)
        {
            let c_name = chek.parent().text();
            if(c_name == option_name)
            {
                return;
            }
        }
        let voting_response_data = {
            args:{
                app:'voting',
                model:'VotingAnswer',
                method:'submit'
            },
            params: {
                voting_id: voting_id,
                voting_option_id: response,
                token: obj_this.token
            }
        }
        function on_success(update_results){
            if (update_results == 'done')                
            {
                obj_this.router.navigate(['/thanks/Response submitted successfully'])
            }
            obj_this.voting_object.my_status = option_name;
            console.log(update_results);
            obj_this.voting_object.chart_data = update_results.chart_data;
            if(obj_this.voting_object.chart_data.length && obj_this.voting_object.public_visibility)                
            {                 
                var chart_colors = window['chart_colors'];
                    var p =0;
                    let question = obj_this.voting_object;
                    for(let j in question.chart_data){
                        if(p>=chart_colors.length)
                        {
                            p = 0;
                        }
                        question.chart_data[j].color = chart_colors[p++];
                    }
                if(update_results.progress_data)
                {
                    obj_this.voting_object.progress_data = update_results.progress_data;
                    window['app_libs']['chart'].load(()=>{
                        window['drawChart'](obj_this.voting_object.progress_data, '#progress-chart');
                    });
                }
                window['app_libs']['chart'].load(()=>{
                    window['drawChart'](obj_this.voting_object.chart_data, '#myChart');
                });
                $('.voting-chart:first').show();
            }
        }
        function submit_response(voting_response_data)
        {
            if (!obj_this.token)
            {
                obj_this.httpService.post(voting_response_data, on_success, null);
            }
            else{
                obj_this.httpService.post_public(voting_response_data, on_success, (err)=>{
                    window['functions'].get_public_feedback(err);
                    return;
                });
            }
        }
        
        if(!obj_this.voting_opened(obj_this.voting_object.open_date)
            || obj_this.voting_closed(obj_this.voting_object.close_date))
        {                        
            if (obj_this.voting_object.signature_required)
            {
                let sign_config = {
                    signature_data: obj_this.voting_object.signature_data,
                    on_signed: function(signature_data){
                        obj_this.voting_object.signature_data = signature_data;
                        voting_response_data.params['signature_data'] = signature_data;
                        submit_response(voting_response_data);
                    }
                }
                window['app_libs']['signature'].load(()=>{
                    window['init_sign'](sign_config);
                });
            }
            else
            {
                submit_response(voting_response_data);
            }                
        }
        else
        {
            window['bootbox'].alert('This Approval/Voting is Closed now.');
        }
    }


    ngOnInit() {
        
    }

    ngOnDestroy() {
        window['voting_id'] = -1;
    }
}