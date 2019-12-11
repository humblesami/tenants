import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { FormsModule }    from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HashLocationStrategy, Location, LocationStrategy } from '@angular/common';

import { FormatTimePipe } from './pipes/format-time.pipe';
import { KeysPipe } from './pipes/keys.pipe';
import { CamelCasePipe } from './pipes/camel.pipe'
import { HourMinutesPipe } from './pipes/hm.pipe'

import { SocketService } from './socket.service';
import { HttpService } from './http.service';
import { RenameService } from './rename.service';
import { UserService } from './user.service';

import { AppComponent }         from './app.component';
import { AppRoutingModule }     from './app-routing.module';
import { AuthGuard } from './auth.guard';

import { RouterModule } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { MentionModule } from 'angular-mentions';
import { NgSelectModule } from '@ng-select/ng-select';
import { NgbModule} from '@ng-bootstrap/ng-bootstrap';
import { DateAgoPipe } from './pipes/date-ago.pipe';
import { StringFirstToUpperPipe } from './pipes/string-first-to-upper.pipe';

import { LoginComponent }   from '../components/login/login.component';
import { HomeComponent }   from '../components/home/home.component';
import { PageNotFound } from './pagenotfound';

import { HeaderComponent } from '../components/header/header.component';
import { ChatComponent } from '../components/chat/chat.component';

import { CommitteesComponent } from '../components/committees/committees.component';
import { CommitteeDetailsComponent } from '../components/committeedetails/committeedetails.component';
import { ProfileDetailsComponent } from '../components/profiledetails/profiledetails.component';
import { ProfilesComponent } from '../components/profiles/profiles.component';
import { MeetingsComponent } from '../components/meetings/meetings.component';
import { MeetingDetailsComponent } from '../components/meetingdetails/meetingdetails.component'
import { ResourcesComponent } from '../components/resources/resources.component'
import { ResourceDetailsComponent } from '../components/resourcedetails/resourcedetails.component';

import { SurveyComponent } from '../components/survey/survey.component';
import { TopicsComponent } from '../components/topics/topics.component';

import { PaginatorComponent } from '../components/paginator/paginator.component';
import { DocumentComponent } from '../components/document/document.component';
import { SettingsComponent } from '../components/settings/settings.component';

import { SetpasswordComponent } from '../components/setpassword/setpassword.component';
import { ForgotpasswordComponent } from '../components/forgotpassword/forgotpassword.component';
import { SigndocComponent } from '../components/signdoc/signdoc.component';
import { CommentsComponent } from '../components/comments/comments.component';
import { MessengerComponent } from '../components/messenger/messenger.component';
import { MessageiconComponent } from '../components/messageicon/messageicon.component';
import { VotingdetailsComponent } from '../components/votingdetails/votingdetails.component';
import { VotingresultsComponent } from '../components/votingresults/votingresults.component';
import { RecordEditComponent } from '../components/recordedit/recordedit.component';
import { VotingsComponent } from '../components/votings/votings.component';
import { EsignDocsComponent } from "src/components/esigndocs/esigndocs.component";
import { EsignDocDetailsComponent } from "src/components/esigndocdetails/esigndocdetails.component";
import { RtcComponent } from '../components/rtc/rtc.component';
import { SurveysComponent } from '../components/surveys/surveys.component';
import { RecorddetailsComponent } from '../components/recorddetails/recorddetails.component';
import { CalendarComponent } from '../components/calendar/calendar.component';
import { BreadcrumbComponent } from '../components/breadcrumb/breadcrumb.component';
import { SurveyresultsComponent } from '../components/surveyresults/surveyresults.component';
import { MeetingresponseComponent } from '../components/meetingresponse/meetingresponse.component';
import { SupportComponent } from '../components/support/support.component';
import { ProfileeditComponent } from '../components/profileedit/profileedit.component';
import { RosterComponent } from '../components/roster/roster.component';
import { ProfilesummaryComponent } from '../components/profilesummary/profilesummary.component';
import {NgxPaginationModule} from 'ngx-pagination';
import { DocumentsComponent } from '../components/documents/documents.component';
import { FoldersComponent } from '../components/folders/folders.component';
import { UserlistComponent } from '../components/userlist/userlist.component';
import { ActionsComponent } from '../components/actions/actions.component';
import { ChatgroupComponent } from '../components/chatgroup/chatgroup.component';
import { UserlistmodalComponent } from '../components/userlistmodal/userlistmodal.component';
import { SearchComponent } from '../components/search/search.component';
import { ViewmembersComponent } from '../components/viewmembers/viewmembers.component';
import { NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
import { MovetomyfolderComponent } from '../components/movetomyfolder/movetomyfolder.component';
import { ThankyouComponent } from '../components/thankyou/thankyou.component';
import { TopiceditComponent } from '../components/topicedit/topicedit.component';
import { EsigndocresultsComponent } from '../components/esigndocresults/esigndocresults.component';
import { FeedbackComponent } from '../components/feedback/feedback.component';

@NgModule({
    imports: [
        AppRoutingModule,
        BrowserModule,
        NgSelectModule,
        FormsModule,        
        HttpClientModule,
        ReactiveFormsModule,
        MentionModule,
        RouterModule,
        RouterTestingModule,
        NgbModule,
        BrowserModule, 
        NgxPaginationModule,
    ],
    declarations: [
        AppComponent,
        HomeComponent,
        LoginComponent,
        PageNotFound,
        HeaderComponent,
        ProfileDetailsComponent,
        ProfilesComponent,
        CommitteesComponent,
        CommitteeDetailsComponent,
        ResourcesComponent,
        ResourceDetailsComponent,
        MeetingsComponent,
        MeetingDetailsComponent,
        SurveyComponent,
        TopicsComponent,
        FormatTimePipe,
        CamelCasePipe,
        HourMinutesPipe,
        PaginatorComponent,
        DocumentComponent,
        SettingsComponent,
        KeysPipe,
        ChatComponent,
        SetpasswordComponent,
        ForgotpasswordComponent,
        SigndocComponent,
        CommentsComponent,
        MessengerComponent,
        MessageiconComponent,
        VotingdetailsComponent,
        VotingresultsComponent,
        RecordEditComponent,
        VotingsComponent,
        EsignDocsComponent,
        EsignDocDetailsComponent,
        RtcComponent,
        SurveysComponent,
        RecorddetailsComponent,
        CalendarComponent,
        BreadcrumbComponent,
        SurveyresultsComponent,
        MeetingresponseComponent,
        SupportComponent,
        ProfileeditComponent,
        DateAgoPipe,
        StringFirstToUpperPipe,
        RosterComponent,
        ProfilesummaryComponent,
        DocumentsComponent,
        FoldersComponent,
        UserlistComponent,
        ActionsComponent,
        ChatgroupComponent,
        UserlistmodalComponent,
        SearchComponent,
        ViewmembersComponent,
        MovetomyfolderComponent,
        ThankyouComponent,
        TopiceditComponent,
        EsigndocresultsComponent,
        FeedbackComponent,
    ],
    providers:[
        AuthGuard,
        SocketService,
        HttpService,
        RenameService,
        UserService,
        Location,
        NgbActiveModal, 
        {provide: LocationStrategy, useClass: HashLocationStrategy}
    ],
    bootstrap: [AppComponent],
    entryComponents: [ChatgroupComponent, UserlistmodalComponent, ViewmembersComponent, RosterComponent, ProfilesummaryComponent, MovetomyfolderComponent,TopiceditComponent]
})
export class AppModule { }
