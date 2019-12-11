import { Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser'
import { HttpService } from '../../app/http.service';
import { SocketService } from '../../app/socket.service';
import { Router } from '@angular/router';

declare var $: any;
@Component({
    selector: 'app-calendar',
    templateUrl: './calendar.component.html',
    styleUrls: ['./calendar.component.css']
})
export class CalendarComponent implements OnInit {
    home_data: any;
    events = [];
    selected_event: any;
    constructor(private httpService: HttpService,
        public router: Router,
        private sanitizer: DomSanitizer,
        private socketService: SocketService) {
            
        }

    ngOnInit() {
        let obj_this = this;
        $('#event-summary .home-calendar-modal-detail>div').hide();
        $('body').on('click', '.fc-event.grid-event', function(){            
            var event_id = $(this).find('.fc-content:first').attr('event_id');
            console.log(obj_this.events, 133, event_id);
            obj_this.selected_event = obj_this.events.filter(function(item){
                return item.id == event_id;
            })
        });
        this.get_home_data();
        $('body').on('click', '.scheduleDetailOpener',function() {
            obj_this.scheduleDetails(this);
        });
    }

    get_home_data() {
        var obj_this = this;
        var success_cb = function(home_data) {
            // console.log(home_data);
            obj_this.home_data = home_data;
            obj_this.show_calendar();
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

    show_calendar() {
        let obj_this = this;
        let home_data = obj_this.home_data;
        var events = [];
        if (obj_this.events.length != 0) {
            events = obj_this.events;
        } else {
            if (home_data.calendar) {                
                home_data.calendar.forEach(function(event: any) {
                    let date = window['dt_functions'].meeting_time_str(event.start);
                    events.push({
                        title: event.name,
                        start: event.start,
                        stop: event.stop,
                        date: date,
                        id: event['id'],
                        my_event: event['my_event']
                    })
                });
                obj_this.events = events;
            }
        }
        // console.log(home_data.calendar,events, obj_this.events);        
        if (home_data.calendar)
        {
            window['app_libs']['moment'].load(()=>{                    
                window['app_libs']['full_calendar'].load(()=>{                        
                    obj_this.renderCalendar(events);
                });
            });
            // if(window['app_libs']['moment'].status != 'loaded')
            // {
            //     window['app_libs']['moment'].load(()=>{                    
            //         window['app_libs']['full_calendar'].load(()=>{                        
            //             obj_this.renderCalendar(events);
            //         });
            //     });
            // }
            // else
            // {
            //     if(window['app_libs']['full_calendar'].status != 'loaded')
            //     {
            //         window['app_libs']['full_calendar'].load(()=>{
            //             obj_this.renderCalendar(events);
            //         });
            //     }
            //     else{
            //         obj_this.renderCalendar(events);
            //     }
            // }
        }
    }

    renderCalendar(events) {
        let obj_this = this;        
        $('#calendar').fullCalendar({
            events: events,
            timezone: 'local',
            eventClick: function(calEvent, jsEvent, view) {
                var id = calEvent.id;
                var req_url = '/meeting/summary'

                let args = {
                    app: 'meetings',
                    model: 'Event',
                    method: 'meeting_summary'
                }
                let input_data = {
                    params: {
                        id: id
                    },
                    args: args
                };
                obj_this.httpService.get(input_data,function(data){
                    obj_this.selected_event = data;
                    $('#calenderModal').modal('show');
                }, null);
            },
            header: {
                left: 'year,month,agendaWeek,agendaDay',
                center: 'title'
            }, // buttons for switching between views
            eventLimit: true, // for all non-agenda views
            // views: {
            //     agenda: {
            //         eventLimit: 6 // adjust to 6 only for agendaWeek/agendaDay
            //     }
            // }
        });

        $('.home-calendar').css('visibility', 'visible');
        let schedule:any;

        if ($('.fc-schedule-button').length == 0) {
            var schedule_html = '<div class="container-fluid schedule-container schedule-wrap">';
            for (var i = 0; i < events.length; i++) {
                if (events[i]['my_event']) {
                    schedule_html += '<div event_id=' + events[i].id + ' class="scheduleDetailOpener row">';
                    // schedule_html += '<div class="col"> <span>' + events[i].date[1] + ' ' + events[i].date[0] +','+ events[i].date[2]+'</span></div>';
                    schedule_html += '<div class="col"> <span>' + events[i].date + '</span></div>';
                    schedule_html += '<div class="col">' + window['dt_functions'].dt_hour_minutes(new Date(events[i].start)) + ' - ' + window['dt_functions'].dt_hour_minutes(new Date(events[i].stop)) + '</div>';
                    schedule_html += '<div class="col">' + events[i].title + '</div>';
                    schedule_html += '</div>'
                }
            }
            schedule_html += '</div>';
            schedule = $(schedule_html);
            var btn = $('<button type="button" class="fc-schedule-button fc-button fc-state-default fc-corner-right">Schedule</button>')
            $('.fc-button-group:first').append(btn);

            btn.click(function showSchedule() {
                $('.schedule-container').show();
                $('.fc-view-container').empty().html(schedule);
                $('.fc-prev-button').hide();
                $('.fc-next-button').hide();
                $('.fc-center').hide();
                $('.fc-today-button').hide();
                $('.fc-state-active').removeClass('fc-state-active');
                btn.addClass('fc-state-active');
            });
        }
        schedule.find('.scheduleDetailOpener').click(function() {
            obj_this.scheduleDetails(this);
        });
    }

    scheduleDetails(el) {
        let obj_this = this;
        var event_id = $(el).attr('event_id');
        let args = {
            app: 'meetings',
            model: 'Event',
            method: 'meeting_summary'
        }
        let input_data = {
            params: {
                id: event_id
            },
            args: args
        };
        obj_this.httpService.get(input_data,function(data){
            // console.log(data, 13888);
            obj_this.selected_event = data;
            $('#calenderModal').modal('show');
        }, null)
    };

    render_CalendarEvnetPopup(result) {
        let obj_this = this;
        var calendar_modal = $('#calenderModal');        
        calendar_modal.modal('show');
    }

    navigate_meeting() {
        var obj_this = this;
        var link = '/upcoming/meeting/' + obj_this.selected_event.id;
        obj_this.router.navigate([link]);
    }
}