import { UserlistmodalComponent } from "src/components/userlistmodal/userlistmodal.component";

declare var $;
export class VideoCall{
    socketService: any;
    constructor(ss: any){
        this.socketService = ss;
    }

    id: any;
    callee: any;
    message: any;
    caller : any;    
    ongoing_call : any;


    timeout = 21000;  
    state = 'available';
    drag_enabled = false;
    is_audio_call = false;            
    incoming_call = undefined;

    make_call(uid, audio_only){
        let video_call = this;
        // console.log(uid, audio_only, 88);
        video_call.drag_enabled = false;        
        if(audio_only)
        {
            video_call.is_audio_call = true;
        }
        else
        {
            video_call.is_audio_call = false;
        }

        var the_user = video_call.socketService.get_user_by_id(uid)
        if(!the_user.online)
        {
            let to = the_user.id;
            let message = video_call.get_missed_call_body();
            video_call.send_messeage(to, message);
            video_call.show_notification(the_user.name +' is not online yet, but will be informed when online')
            return;
        }
        let call_id = video_call.socketService.user_data.id+'-'+uid+'-call';                
        video_call.caller = video_call.socketService.user_data;
        video_call.callee = the_user;
        video_call.id = call_id; 
        let data =  {
            caller_id: video_call.socketService.user_data.id,
            callee_id: uid,
            call_id : call_id,
            is_audio_call : video_call.is_audio_call
        };

        // console.log(video_call.caller, video_call.callee);
        if(the_user.online){
            video_call.socketService.emit_rtc_event('incoming_call', data, [uid]);                    
            video_call.message = 'Calling...';
        }
        else
        {
            video_call.message = "Called person is not online but will be informed about your call when he/she will be online";                    
        }
        video_call.state = 'outgoing';
        video_call.initialize_call();
        
        
        setTimeout(function(){
            // console.log(video_call.state, video_call.callee.id, 727);
            if(video_call.state == 'outgoing')
            {
                video_call.cancel('no response');
            }
        }, video_call.timeout);        
    }

    init(uid, audio_only){        
        let obj_this = this;        
        window['app_libs']['rtc'].load(function(){
            obj_this.make_call(uid, audio_only);
        })
    }

    show_incoming_call(data){
        console.log('got call');
        var video_call = this;        
        if(video_call.ongoing_call || video_call.state != 'available')
        {
            // video_call.show_notification('Another incoming call');
            video_call.reject(data);
            return;
        }
        // console.log(data, 1334);
        video_call.state = 'incoming';
        video_call.id = data.call_id;
        video_call.is_audio_call = data.is_audio_call;
        video_call.caller = video_call.socketService.get_user_by_id(data.caller_id);
        video_call.callee = video_call.socketService.user_data;
        window['app_libs']['rtc'].load(function(){
            video_call.initialize_call();
        });
    }

    accept(){
        var video_call = this;
        video_call.im_caller = false;
        var data = { 
            user_id: video_call.socketService.user_data.id
        };        
        video_call.socketService.emit_rtc_event('accepted', data, [video_call.caller.id]);
        video_call.state = 'accepted';
        video_call.message = 'Connecting caller';
    }

    im_caller = false;
    

    start_for_me(data){
        // console.log(data, 156);
        var video_call = this;
        video_call.state = 'ongoing';        
        if(!video_call.id)
        {
            console.log(video_call.state, 'Invalid call id, it must has been alreasy set');
            // console.log(video_call, video_call.incoming);
            return;
        }
        
        var params = {
            uid: video_call.socketService.user_data.id,
            room: video_call.id,                    
            token: video_call.socketService.user_data.token
        };    
        // console.log(params, 1577);
        if(!video_call.socketService.rtc_multi_connector)
        {
            video_call.socketService.rtc_multi_connector = window['video_caller'];
        }
        video_call.ongoing_call = video_call.id;
        // console.log(video_call.socketService.rtc_multi_connector, 190);

        var on_started = function(){
            video_call.maximize();
        };
        if(video_call.caller.id == params.uid)
        {
            on_started = function(){
                video_call.participants = [video_call.caller, video_call.callee];
                if(data)
                {
                    data = {
                        create_time: Date(), 
                        room: video_call.id,
                        user_id: data.user_id
                    }
                    // console.log(data, 14889);
                    video_call.socketService.emit_rtc_event('started_by_caller', data, [data.user_id]);
                    video_call.im_caller = true;
                }
                video_call.maximize();
            }
        }
        $('#rtc-container').addClass('ongoing_call');
        video_call.socketService.rtc_multi_connector.init(params, on_started, video_call.is_audio_call);        
    }
    
    

    cancel(message=undefined){
        let video_call = this;
        // console.log('Cancelling', this.caller.id, this.callee.id);
        video_call.socketService.emit_rtc_event('cancelled', '', [video_call.callee.id]);
        this.quit(message);
    }

    cancelled(data){
        // console.log('Cancelled', this.caller.id, this.callee.id);
        this.quit();
    }

    reject(data=undefined){
        var video_call = this;
        var audience = []
        if(data)
        {
            audience = [data.caller_id];
            data = { message: 'User is busy in an other call ', already_in_call:true, callee_id: data.callee_id};
        }
        else{
            audience = [video_call.caller.id]
            data = { message: 'Sorry busy'}
        }
        if(!video_call.caller.id)
        {
            console.log('No caller id to send in reject');
        }
        video_call.socketService.emit_rtc_event('rejected', data, audience);
        if(!data.already_in_call)
        {
            video_call.quit();
        }
    }


    

    terminate(){
        let video_call = this;
        var data = { 
            user_id: video_call.socketService.user_data.id, 
            room_id: this.id
        };
        video_call.socketService.socket.emit('call_terminated', data);
        // console.log(video_call.ongoing_call, this, 568);
        this.quit('terminating');
    }

    terminated(data){
        let video_call = this;
        if(video_call.ongoing_call)
        {
            console.log('Leaving now');
            // console.log(video_call.ongoing_call, this, 189);
            this.quit();
        }
        else
        {
            console.log('Already left');
        }
    }

    toggle_camera(){
        let video_call = this;
        try{
            video_call.socketService.rtc_multi_connector.toggle_camera();
        }
        catch(er){
            console.log(14, er);
        }                
        // 
    }

    quit(request_type=undefined){

        let video_call = this;
        video_call.im_caller = false;
        // console.log(video_call.ongoing_call, request_type, 193);
        if(video_call.ongoing_call && request_type != 'terminating')
        {
            video_call.terminate();
        }
        video_call.drag_enabled = false;
        let to = video_call.callee.id;
        video_call.caller = undefined;
        video_call.callee = undefined;
        if(video_call.ongoing_call)
        {
            try{
                video_call.socketService.rtc_multi_connector.stop_my_tracks();
                video_call.socketService.rtc_multi_connector.socket.disconnect();                        
            }
            catch(er)
            {
                console.log('error in rtc end call', er);
            }                    
        }
        
        video_call.state = 'available';
        video_call.ongoing_call = undefined;                 
        $('#videos-container').html('');
        $('#rtc-container').removeClass('ongoing_call').hide();
        if (request_type == 'no response')
        {
            if (video_call.id)
            {
                let message = video_call.get_missed_call_body();
                // let message = 'missed call from ' + from;
                video_call.send_messeage(to,message)
            }
        }
    }

    get_missed_call_body()
    {
        return `<div class="missed-call">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="15.458" viewBox="0 0 20.899 15.458">
                    <g id="missed-call-phone-receiver-with-left-arrow" transform="translate(0 -80.325)">
                        <g id="phone-missed" transform="translate(0 80.325)">
                            <path id="Path_8723" data-name="Path 8723" d="M5.613,82.484l4.75,4.75,6.045-6.045-.864-.864-5.182,5.182L6.477,81.62H9.5v-1.3H4.318v5.182h1.3Zm14.854,9.672a14.606,14.606,0,0,0-20.208,0,.835.835,0,0,0,0,1.209l2.159,2.159a.784.784,0,0,0,.6.259.784.784,0,0,0,.6-.259,11.3,11.3,0,0,1,2.332-1.641.993.993,0,0,0,.518-.777V90.429a11.965,11.965,0,0,1,3.973-.6,14.707,14.707,0,0,1,3.973.6v2.677a.83.83,0,0,0,.518.777,8.765,8.765,0,0,1,2.332,1.641.835.835,0,0,0,1.209,0l2.159-2.159a.784.784,0,0,0,.259-.6C20.9,92.5,20.64,92.329,20.467,92.156Z" transform="translate(0 -80.325)" fill="#ffffff"/>
                        </g>
                    </g>
                </svg>
                <span>missed a call</span>
                </div>`;
    }

    send_messeage(to, message)
    {
        var date = new Date();
        var components = [
            date.getFullYear(),
            date.getMonth(),
            date.getDate(),
            date.getHours(),
            date.getMinutes(),
            date.getSeconds(),
            date.getMilliseconds()
        ];
        var timestamp = components.join("");        
        var input_data = {
            body: message,
            uuid : timestamp,
            attachments: [],
			to: to,
            create_date: new Date(),
            no_loader: 1,
            message_type: 'notification'
        };
        let args = {
            app: 'chat',
            model: 'message',
            method: 'send',
            no_loader:1,
        }
        try{
            var options =
            {
                data:{
                    params: input_data,
                    args : args
                }
            }
            window['dn_rpc_object'](options);
        }
        catch(er)
        {
            console.log(er)
        }
    }

    initialize_call(){
        this.maximize();
        $('#rtc-container').show();
    }
    accepted(data){
        this.start_for_me(data);        
    }

    started_by_caller(data){
        let video_call = this;
        video_call.start_for_me(data);
    }
    
    same(val){
        return val;
    }

    rejected(data){
        let video_call = this;
        if(video_call.state == 'outgoing')
        {
            if (data.already_in_call)
            {
                let message = video_call.get_missed_call_body();
                console.log(video_call.callee.id, data.callee_id, 666);
                video_call.send_messeage(video_call.callee.id, message);
                video_call.show_notification('User is busy in another call');
            }
            else
            {
                video_call.show_notification('User is busy, try later');
            }
        }
        else
        {
            console.log(video_call.state, ' Not calling how cancelled');
        }
        video_call.quit(data.message);
    }

    toggle_size(){
        if($('#rtc-container').hasClass('full')){
            this.minimize();
        }
        else{
            this.maximize();
        }
    }

    minimize(){
        var rtc_container = $('#rtc-container');
        rtc_container.css({left: 'unset', top: 'unset', bottom : 0, right: 0});
        rtc_container.removeClass('min').removeClass('full').addClass('min');
        window['rtc-call-max'] = 0;        
        if(rtc_container.hasClass('ui-draggable'))
        {
            rtc_container.draggable('enable');
        }
        else{
            rtc_container.draggable({'containment':[0, 0, window.innerWidth - 20, window.innerHeight - 20]});
        }
        if($('.media-container.self:first').hasClass('ui-draggable')){
            $('.media-container.self:first').draggable('disable');
        }
    }

    maximize(){
        // console.log(3444);
        var rtc_container = $('#rtc-container');
        rtc_container.css({left: 'unset', top: 'unset', bottom : 0, right: 0});
        if(rtc_container.hasClass('ui-draggable'))
        {
            rtc_container.draggable('disable');
        }
        if($('.media-container.self:first').hasClass('ui-draggable')){
            $('.media-container.self:first').draggable('enable');    
        }
        else{
            $('.media-container.self:first').draggable({'containment':[0, 0, window.innerWidth - 20, window.innerHeight - 20]});
        }
        $('.media-container.self:first').css({top: '30px', left: '10px'});
        rtc_container.removeClass('min').removeClass('full').addClass('full');
        window['rtc-call-max'] = 1;
    }

    show_users() {
        let obj_this = this;
        var on_modal_closed = function(result){
            console.log(result, 444);
            obj_this.participants = result;
        };

        var diaolog_options = {
            call_back: on_modal_closed,
            selected_users: obj_this.participants,
            component: UserlistmodalComponent,
            extra_input: { add_only: 1 }
        }
        obj_this.socketService.user_selection_dialog(diaolog_options);
    }

    participants = undefined;

    add_participants() {
        
    }

    show_notification(message){
        window['bootbox'].alert(message);
        setTimeout(function(){
            $('.bootbox.modal.fade.bootbox-alert.show').css('display','flex');
        },151);                
    }
}