import { Component, OnInit } from '@angular/core';
import {HttpService} from '../../app/http.service';
import {ActivatedRoute} from '@angular/router';
import {BreadcrumbComponent} from '../breadcrumb/breadcrumb.component';
declare var $: any;

@Component({
    selector: 'app-votingresults',
    styleUrls:['./votingresults.css'],
    templateUrl: './votingresults.component.html',
})

export class VotingresultsComponent implements OnInit {
    surveyDetails: any;
    bread_crumb = {
        items: [],
        title: ''
    };

    constructor(private httpService: HttpService, private route: ActivatedRoute, ) {}

    ngOnInit() {
        const obj_this = this;
        const page_url = window.location + '';
        window["functions"].showLoader('survey-iframe');

        let cookie = window['current_user'].cookie
        
        let voting_id = obj_this.route.snapshot.params.id;
        let voting_url = window["site_config"].server_base_url + '/voting/graphical/a-'+voting_id+'/'+cookie.id+'/' + cookie.token + '/' + cookie.db;
        console.log(voting_url);
        $('#survey-iframe').attr('src', voting_url);
        $('#survey-iframe').load(function() {
            window["functions"].hideLoader('survey-iframe');
        });
        
        let args = {
            app: 'voting',
            model: 'Voting',
            method: 'get_details'
        }			
        let final_input_data = {
            params: { id: voting_id },
            args: args
        };
        obj_this.httpService.get(final_input_data,
            (result: any) => {
                obj_this.surveyDetails = result;

                this.bread_crumb.title = this.surveyDetails['title'];
                // if (page_url.indexOf('home') !== -1) {
                //     this.bread_crumb.items.push({
                //         title: 'Home',
                //         link: '/'
                //     });
                // }
                if (obj_this.surveyDetails['meeting_name'] && obj_this.surveyDetails['meeting_id']) {
                    this.bread_crumb.items.push({
                        title: obj_this.surveyDetails['meeting_name'],
                        link: '/meeting/' + obj_this.surveyDetails['meeting_id']
                    });
                }
                if (obj_this.surveyDetails['topic_name'] && obj_this.surveyDetails['topic_id']) {
                    this.bread_crumb.items.push({
                        title: obj_this.surveyDetails['topic_name'],
                        link: '/topic/' + obj_this.surveyDetails['topic_id']
                    });
                }
            },
            (error: any) => {}
        );
    }
}