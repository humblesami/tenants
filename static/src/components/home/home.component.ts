import { Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser'
import { HttpService } from '../../app/http.service';
import { SocketService } from '../../app/socket.service';
import { Router } from '@angular/router';
import { UserlistComponent } from '../userlist/userlist.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

declare var $: any;
@Component({
    styleUrls:['./home.css'],
    templateUrl: 'home.component.html'    
})
export class HomeComponent implements OnInit {
    to_do_data = false;
    to_do_count = 0;
    date: Number = Date.now();
    home_data: any;

    constructor(private httpService: HttpService,
        public router: Router,
        private sanitizer: DomSanitizer,
        private socketService: SocketService,
        private modalService: NgbModal) {            
        $('#collapsibleNavbar').children().eq(0).addClass('active');
    }

    text_limit = 1250;

    navigate_meeting() {
        var obj_this = this;
        let id = document.getElementsByClassName('go_details')[0].id;
        obj_this.router.navigate(['/upcoming/meeting/' + id]);
    }

    scroll_to_do(){
        if(!this.home_data)
        {
            return;
        }
        $('.router-outlet').animate({            
            scrollTop: $('#to-do').position().top - 20
        }, 500);
    }    

    get_home_data() {
        var obj_this = this;
        var success_cb = function(home_data) {
            if (!home_data['to_do_items']) {
                console.log("invalid data", home_data);
                return;
            }
            var result = home_data.to_do_items.pending_meetings;
            for (var i in result) {
                var start = result[i]['start'];
                start = window['dt_functions'].meeting_time(start);
                result[i]['start_dt'] = start;
            }
            for(var survey of home_data.to_do_items.pending_surveys)
            {
                survey.open_date = window['dt_functions'].meeting_time(survey.open_date);
            }
            for(var voting of home_data.to_do_items.pending_votings)
            {
                voting.open_date = window['dt_functions'].meeting_time(voting.open_date);
            }
            
            home_data.text = home_data.news.description;
            home_data.news.description = home_data.news.description.substr(0,obj_this.text_limit);
            if(home_data.text.length > obj_this.text_limit){
                home_data.news.description = home_data.news.description +'... <a id="readmore" class="readmore">Read More</a>';                
            }
            home_data.description = obj_this.sanitizer.bypassSecurityTrustHtml(home_data.news.description);
            if(home_data.text.length > obj_this.text_limit){
                setTimeout(function(){
                    $('#readmore').click(function(){
                        obj_this.show_answer_details();
                    })
                },10);
            }            
            
            var valid_videos = [];            
            home_data.video_ids.forEach((element: any) => {
                element.original_url = element.url;
                if (element.url.match(/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g)) {
                    element.url = obj_this.sanitizer.bypassSecurityTrustResourceUrl(element.url);
                    valid_videos.push(element);
                } else {
                    // console.log(element.url + ' is not a valid url for video '+element.name);
                }
            });            
            obj_this.home_data = home_data;
            home_data.video_ids = valid_videos;
            var to_do_items = home_data.to_do_items;
            //console.log(home_data);
            obj_this.to_do_count = to_do_items.pending_documents.length + to_do_items.pending_surveys.length + to_do_items.pending_votings.length;
        };
        let args = {
            app: 'meetings',
            model: 'News',
            method: 'get_data'
        }
		let input_data = {
            params: {},
            args: args
        };
        obj_this.httpService.get(input_data, success_cb, null);
    }

    show_answer_details(){
        // console.log(this.home_data.description.changingThisBreaksApplicationSecurity);
        window['bootbox'].alert(this.home_data.text);
        $('.modal-dialog').addClass("modal-lg");   
        $('.bootbox-body').addClass('bootbox-body-scroll');     
    }
    view_video(video_name, video_url){
        $('#videoModal .modal-heaer').html('<h3>'+video_name+'</h3>')
        $('#videoModal .modal-body .embed-responsive').html(`
            <iframe class="embed-responsive-item" frameborder="0"  allowfullscreen="allowfullscreen"
            src="`+video_url+`?autoplay=1">
            </iframe>
        `);     
        $('#videoModal').modal('show');
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
        console.log(this.visible_limit[item_type],this.start_indices[item_type],items,item_type);
    }

    open() {
        let obj_this = this;
		const modalRef = this.modalService.open(UserlistComponent, { keyboard: false, backdrop: 'static' });
        modalRef.componentInstance.input_users = [];
		modalRef.result.then((result) => {
            if (result){
                console.log(result);
            }
        });
    }
    
    ngOnInit() {
        var obj_this = this;
        $('.home-container').show();
        $('#videoModal').on('hidden.bs.modal', function () {
            console.log(43434);
            $('#videoModal .modal-body .embed-responsive').html('');
        });

        obj_this.text_limit = parseInt(""+ ($(window).width()));
        // console.log(obj_this.text_limit, 122);
        obj_this.get_home_data(); 
        $(function(){
            obj_this.ng_init = true;
        })
        this.socketService.server_events['to_do_item_updated'] = function() {
            if (obj_this){
                setTimeout(function(){
                    obj_this.get_home_data();
                },5000)
            }                
        }   
        
        var vw = $(window).width();
        // console.log(vw , 66);
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
        // console.log(obj_this.visible_limit, obj_this.ending_indices,1122);
    }
}