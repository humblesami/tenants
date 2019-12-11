if(window['site_config'].log_loading)
{
    console.log('Init Routing '+window['dt_functions'].now());
}
import {CommentsComponent} from "../components/comments/comments.component";

declare var $: any;

import { NgModule } from '@angular/core';
import { Routes, Router,RouterModule, RoutesRecognized, NavigationStart, NavigationEnd} from '@angular/router';

import { AuthGuard } from './auth.guard';
import { PageNotFound } from './pagenotfound';

import {SocketService} from './socket.service';

import { HomeComponent } from '../components/home/home.component';
import { CalendarComponent } from '../components/calendar/calendar.component';
import { LoginComponent } from '../components/login/login.component';

import { ForgotpasswordComponent } from '../components/forgotpassword/forgotpassword.component';

import { CommitteesComponent } from '../components/committees/committees.component';
import { CommitteeDetailsComponent } from '../components/committeedetails/committeedetails.component';
import { MeetingsComponent } from '../components/meetings/meetings.component';
import { MeetingDetailsComponent } from '../components/meetingdetails/meetingdetails.component';
import { ProfileDetailsComponent } from '../components/profiledetails/profiledetails.component';
import { ProfileeditComponent } from '../components/profileedit/profileedit.component';
import { ProfilesComponent } from '../components/profiles/profiles.component';
import { ResourcesComponent } from '../components/resources/resources.component';
import { ResourceDetailsComponent } from '../components/resourcedetails/resourcedetails.component';

import { SurveyComponent } from '../components/survey/survey.component';
import { TopicsComponent } from '../components/topics/topics.component';
import { DocumentComponent } from '../components/document/document.component';
import { SettingsComponent } from '../components/settings/settings.component';
import { SetpasswordComponent } from '../components/setpassword/setpassword.component';
import { SigndocComponent } from 'src/components/signdoc/signdoc.component';
import { ChatComponent } from 'src/components/chat/chat.component';
import {MessengerComponent} from "../components/messenger/messenger.component";
import { VotingdetailsComponent } from '../components/votingdetails/votingdetails.component';
import { VotingresultsComponent } from "src/components/votingresults/votingresults.component";
import { RecordEditComponent } from '../components/recordedit/recordedit.component';
import { RecorddetailsComponent } from '../components/recorddetails/recorddetails.component';
import { VotingsComponent } from '../components/votings/votings.component'
import { EsignDocsComponent } from "src/components/esigndocs/esigndocs.component";
import { EsignDocDetailsComponent } from "src/components/esigndocdetails/esigndocdetails.component";
import { RtcComponent } from '../components/rtc/rtc.component';
import { SurveysComponent } from '../components/surveys/surveys.component'
import { SurveyresultsComponent } from '../components/surveyresults/surveyresults.component'
import { SupportComponent } from '../components/support/support.component';
import { UserlistComponent } from '../components/userlist/userlist.component';
import { HttpService } from "./http.service";
import { ActionsComponent } from "src/components/actions/actions.component";
import { ThankyouComponent } from '../components/thankyou/thankyou.component';
import { FeedbackComponent } from '../components/feedback/feedback.component';
import { EsigndocresultsComponent } from "src/components/esigndocresults/esigndocresults.component";


const appRoutes: Routes = [    
    { path: 'login', component: LoginComponent},
    { path: 'logout', component: LoginComponent},
    
    { path: '', component: HomeComponent, canActivate: [AuthGuard]},
    { path: 'calendar', component: CalendarComponent, canActivate: [AuthGuard]},

	{ path: 'forgot-password', component: ForgotpasswordComponent},
    { path: 'set-password', component: SetpasswordComponent},
    { path: 'reset-password/:token', component: SetpasswordComponent},
    { path: 'thanks/:message', component: ThankyouComponent},
    { path: 'feedback/:message', component: FeedbackComponent},

    { path: 'my-profile', component: ProfileDetailsComponent, canActivate: [AuthGuard]},
    { path: 'my-profile/edit', component: ProfileeditComponent, canActivate: [AuthGuard]},	
    { path: 'profiles', data:{app:'meetings', model: 'Profile'}, component: ProfilesComponent, canActivate: [AuthGuard]},

    { path: 'profiles/directors', data:{app:'meetings', model: 'Profile'}, component: ProfilesComponent, canActivate: [AuthGuard]},
    { path: 'profiles/admins', data:{app:'meetings', model: 'Profile'}, component: ProfilesComponent, canActivate: [AuthGuard]},
    { path: 'profiles/staff', data:{app:'meetings', model: 'Profile'}, component: ProfilesComponent, canActivate: [AuthGuard]},
        
    { path: 'profile/:id', component: ProfileDetailsComponent, canActivate: [AuthGuard]},

    { path: 'director/:id', component: ProfileDetailsComponent, canActivate: [AuthGuard]},
    { path: 'admin/:id', component: ProfileDetailsComponent, canActivate: [AuthGuard]},
    { path: 'staff/:id', component: ProfileDetailsComponent, canActivate: [AuthGuard]},
    
    { path: 'committees', data:{app:'meetings', model: 'Committee'}, component: CommitteesComponent, canActivate: [AuthGuard]},
    { path: 'committees/:id', component: CommitteeDetailsComponent, canActivate: [AuthGuard]},

	{ path: 'resources', data:{app:'resources', model: 'Folder', search_models:{resources: ['Folder', 'ResourceDocument']} }, component: ResourcesComponent, canActivate: [AuthGuard]},
	{ path: 'meetings/archived', data:{app:'meetings', model: 'Event', search_models:{meetings: ['Event','Topic','MeetingDocument','AgendaDocument']} }, component: MeetingsComponent, canActivate: [AuthGuard]},
	{ path: 'meetings/completed', data:{app:'meetings', model: 'Event', search_models:{meetings: ['Event','Topic','MeetingDocument','AgendaDocument']} }, component: MeetingsComponent, canActivate: [AuthGuard]},
    { path: 'meetings/upcoming',data:{app:'meetings', model: 'Event', search_models:{meetings: ['Event','Topic','MeetingDocument','AgendaDocument']} }, component: MeetingsComponent, canActivate: [AuthGuard]},
    { path: 'meetings/draft', data:{app:'meetings', model: 'Event', search_models:{meetings: ['Event','Topic','MeetingDocument','AgendaDocument']}}, component: MeetingsComponent, canActivate: [AuthGuard]},

	{ path: 'upcoming/meeting/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
	{ path: 'completed/meeting/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
	{ path: 'draft/meeting/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
    { path: 'meeting/archived/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
    { path: 'meeting/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
	
	{ path: 'resource/:id', component: ResourceDetailsComponent, canActivate: [AuthGuard]},
	{ path: 'home/meeting/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
	{ path: 'survey/:id', component: SurveyComponent, canActivate: [AuthGuard]},
	{ path: 'home/survey/:id', component: SurveyComponent, canActivate: [AuthGuard]},
	{ path: 'topic/:id',  component: TopicsComponent, canActivate: [AuthGuard]},
	
    { path: 'signature/doc/:res_id', component: SigndocComponent, canActivate: [AuthGuard]},
    
    { path: ':doc_type/doc/:res_id', component: DocumentComponent, canActivate: [AuthGuard]},    
    { path: ':doc_type/doc/:res_id/:kw', component: DocumentComponent, canActivate: [AuthGuard]},
    { path: 'iframe/:doc_type/:res_id/:token', component: DocumentComponent},

    { path: 'chat', component: ChatComponent, canActivate: [AuthGuard]},
    { path: 'messenger', component: MessengerComponent, canActivate: [AuthGuard]},

    
    { path: 'comments/:res_modal', component: CommentsComponent, canActivate: [AuthGuard]},    

	{ path: 'settings', component: SettingsComponent, canActivate: [AuthGuard]},    

	{ path: 'meetings/completed/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
    { path: 'meetings/archived/:id', component: MeetingDetailsComponent, canActivate: [AuthGuard]},
    { path: 'public-meeting/:id/:token', component: MeetingDetailsComponent},
	
    { path: 'edit/:app/:model/:id/:action', component: RecordEditComponent, canActivate: [AuthGuard]},
    { path: 'edit/:app/:model/add', component: RecordEditComponent, canActivate: [AuthGuard]},
    { path: ':app/:model/details/:id', component: RecorddetailsComponent, canActivate: [AuthGuard]},
            

    { path: 'surveys', data:{app:'survey', model:'Survey', search_models: {survey: ['Survey','Question']} }, component: SurveysComponent, canActivate: [AuthGuard]},    
    { path: 'signdocs', data:{app:'esign', model:'SignatureDoc'}, component: EsignDocsComponent, canActivate: [AuthGuard]},
    { path: 'votings', data:{app:'voting', model:'Voting', search_models:{ voting:['Voting','VotingChoice','VotingType']} }, component: VotingsComponent, canActivate: [AuthGuard]},
    
    { path: 'actions', data:{app:'voting', model:'Voting', search_models:{survey:['Survey', 'Question'], esign: ['SignatureDoc'],voting: ['Voting','VotingChoice','VotingType']}}, component: ActionsComponent, canActivate: [AuthGuard]},

    { path: 'voting/:id', component: VotingdetailsComponent, canActivate: [AuthGuard]},
    { path: 'public-voting/:id/:token', component: VotingdetailsComponent},
    { path: 'voting/:id/results', component: VotingresultsComponent},
    { path: 'survey/:id/results', component: SurveyresultsComponent},
    { path: 'signdoc/:id', component: EsignDocDetailsComponent, canActivate: [AuthGuard]},
    { path: 'signdoc/:id/results', component: EsigndocresultsComponent, canActivate: [AuthGuard]},
    { path: 'token-sign-doc/:id/:token', component: EsignDocDetailsComponent},

    { path: 'support', component: SupportComponent},
    { path: 'rtc', component: RtcComponent},
    { path: 'users', component: UserlistComponent},
	// otherwise redirect to home
	{ path: '**', component: PageNotFound }
];

var site_functions = window['functions'];

let routing_options = {
    imports: [RouterModule.forRoot(appRoutes, {useHash: true})],    
    exports: [RouterModule],
};

@NgModule(routing_options)
export class AppRoutingModule {
	constructor(private router: Router, private socketService: SocketService, httpService: HttpService) {
        var crouter = router;
		router.events.subscribe((event) => {
			if (event instanceof NavigationStart) {
                // console.log(event, router.routerState);
                httpService.search_kw = '';
                httpService.offset = 0;
                socketService.init_route(event.url);
				$('.hidemouseaway').hide();
                $('.searchbar-full-width').hide();
                $('.modal:visible button.close:first').click();
                socketService.search_bar_shown = false;
                site_functions.showLoader('Route');
                $('body').removeClass('pdf-viewer');                
                window['pathname'] = event.url;
                if(window['on_annotator_unload'])
                {
                    window['on_annotator_unload']();
                }
			}
			else if (event instanceof NavigationEnd) {                
                var next_url = event.url;
                var current_url = localStorage.getItem('current_url');
                if(!current_url)
                {
                    current_url = next_url;
                }
                localStorage.setItem('previous_url', current_url);
                localStorage.setItem('current_url', next_url);
                site_functions.hideLoader('Route');
                $('ul.app-menu:first a.active').removeClass('active');
                $('ul.app-menu:first a[routerLink="'+next_url+'"]').addClass('active');
                
            }
            else if (event instanceof RoutesRecognized) {                
                let route = event.state.root.firstChild;                
                socketService.route_changed(route);
            }
		});
	}
}