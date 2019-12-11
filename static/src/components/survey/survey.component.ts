import { Component, OnInit } from '@angular/core';
import {HttpService} from '../../app/http.service';
import {ActivatedRoute} from '@angular/router';
import {Router} from '@angular/router';
declare var $: any;

@Component({
	selector: 'survey',
	styleUrls:['./survey.css', '../votingdetails/meetingdetails.css'],
    templateUrl: './survey.component.html'
})
export class SurveyComponent implements OnInit {
    surveyDetails :any ;
    bread_crumb = {
        items: [],
        title: ''
    };

	constructor(private httpService : HttpService, private route: ActivatedRoute,
		public router: Router,) { }

	ngOnInit() {
		const obj_this = this;
        const page_url = window.location + '';
        window["functions"].showLoader('survey-iframe');
		let args = {
            app: 'survey',
            model: 'Survey',
            method: 'get_details'
        }			
        let final_input_data = {
            params: { survey_id: obj_this.route.snapshot.params.id },
            args: args
        };
        obj_this.httpService.get(final_input_data,
			(result: any) => {
				obj_this.surveyDetails = result;
				//dconsole.log(result)
					window["functions"].hideLoader('survey-iframe');
				// if(obj_this.surveyDetails['url']){
                //     $('#survey-iframe').attr('src',obj_this.surveyDetails['url']);
                //     $('#survey-iframe').load(function(){
                //         window["functions"].hideLoader('survey-iframe');
                //     });
				// }

				this.bread_crumb.title = obj_this.surveyDetails['name'];
				if (page_url.indexOf('home') !== -1) {
					this.bread_crumb.items.push({ title: 'Home', link: '/' });
				}
				if (obj_this.surveyDetails['meeting_name'] && obj_this.surveyDetails['meeting_id']) {
					this.bread_crumb.items.push({
						title: obj_this.surveyDetails['meeting_name'],
						link: '/meeting/' + obj_this.surveyDetails['meeting_id']
					});
				}
			},
			(error: any) => {
				obj_this.router.navigate(['/surveys'])
			});
	}
}
