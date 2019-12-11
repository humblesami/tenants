var time_out_session = undefined;
var session_time_limit = 1800000;
var is_mobile_device = undefined;
var is_local_host = false;
var server_wait_loader = undefined;
var loader_last_shown = undefined;

function location_obj(){    
    return window.location;
}
function location_now(){ 
    return location_obj().toString();
}
function origin_now(){
    return location_obj().origin.toString();
}

var dn_current_site_user = {
    cookie: {
        token: "",
        name: "",
        id: undefined,
        photo: false
    },
    socket: {},
    time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    onLogin: function(data) {
        dn_current_site_user.cookie = data;
        data = JSON.stringify(data);
        localStorage.setItem('user', data);
        refreshSession();
        localStorage.setItem('last_activity', Date());        
        $('.popup.messenger').hide();
        $('body').removeClass('public').addClass('user');
    },
    logout: function(navigate) {
        if(location_now().endsWith('user/login'))
        {
            return;
        }
        if(!dn_current_site_user.cookie)
        {
            return;
        }
        if(location_now().indexOf('login') == -1)
        {
            $('body').hide();
            window['auth_js'].add_public_class();
        }
        localStorage.removeItem("user");
        dn_current_site_user.cookie = undefined;
        if (window['socket_manager']) {
            window['socket_manager'].set_admin_mode(false);
            window['socket_manager'].close_socket();
            window['socket_manager'].user_data = undefined;
        }
        bootbox.hideAll();
    },
    initUserDataFromCookie: function() {
        var user_info = localStorage.getItem("user");
        try {
            if (user_info) {
                user_info = JSON.parse(user_info);
                dn_current_site_user.cookie = user_info;
            }
        } catch (er) {
            console.log(er);
        }
    }
};



var site_functions = {
    processes: [],
    get_public_feedback: function(res){
        if(res && res.error)
        {
            res = res.error;
        }
        if (typeof res == 'string')
        {
            if(res.length > 200)
            {
                console.log(res);
                res = 'Invalid operation';                
            }
            window.location = '/#/feedback/'+res;
            return true;
        }
        else{            
            return false;
        }
    },
    get_path_name: function() {
        if(location_now().indexOf('localhost') > -1)
        {
            is_local_host = true;
        }
        if (location_obj().hash) {
            window['pathname'] = location_obj().hash.substr(1, location_obj().hash.length);
        } else {
            window['pathname'] = location_obj().toString().replace(origin_now(), '');
        }
        return window['pathname'];
    },
    readFiles: function(files, on_drop){
        for (var i = 0; i < files.length; i++) {
            var file_name = files[i].name;
            // document.getElementById('fileDragName').value = files[i].name;
            // document.getElementById('fileDragSize').value = files[i].size
            // document.getElementById('fileDragType').value = files[i].type
            reader = new FileReader();
            reader.onload = function(event) {
                console.log('file name ='+ file_name);
                if(on_drop)
                {
                    on_drop({name: file_name, data: event.target.result});
                }
            }
            reader.readAsDataURL(files[i]);
        }
    },
    go_to_login: function(force) {        
        if(location_now().indexOf('/login') > -1)
        {
            return;
        }
        if(!force && location_now().indexOf('localhost:4200') > -1)
        {
            return;
        }
        localStorage.removeItem('user');
        window['auth_js'].add_public_class();
        if(dn_current_site_user.cookie && dn_current_site_user.cookie.token)
        {
            dn_current_site_user.logout();
        }
        if(!location_now().endsWith('login'))
        {
            if(location_now().indexOf('4200') == -1)
            {
                window.location = '/user/login';
            }
            else{
                window.location = '/#/login';
            }
        }
    },


    get_file_binaries(files, resolve){
        var res_binaries = [];
        var len = files.length;
        for (var i = 0; i < files.length; i++) {
            setupReader(files[i]);
        }
        function setupReader(file) {
            var name = file.name;
            var reader = new FileReader();
            reader.onload = function(){
                var dataURL = reader.result;
                res_binaries.push({
                    name: name,
                    binary : dataURL
                });
                if(res_binaries.length == len)
                {
                    resolve(res_binaries);
                }
            };
            reader.readAsDataURL(file);
        }
    },

    
    loadingTimeOut: undefined,
    showLoader: function(nam) {
        var obj_this = this;
        if (obj_this.processes.length == 0) {
            server_wait_loader.show();
            server_wait_loader.shown = 1;
        }
        if(obj_this.loadingTimeOut)
        {
            clearTimeout(obj_this.loadingTimeOut);
        }
        loader_last_shown = new Date();
        obj_this.loadingTimeOut = setTimeout(function() {
            if(obj_this.processes.length)
            {
                obj_this.hideLoader('force', 'Timeout');
            }
            else
            {
                clearTimeout(obj_this.loadingTimeOut);
            }
        }, 29000);
        obj_this.processes.push(nam);
        var loading_text = 'Loading '+this.processes.join(',');
        if(site_config.log_loading)
        {
            console.log('Added '+nam+ ' '+window['dt_functions'].now());
        }
        server_wait_loader.find('.text').html(loading_text);
        //console.log(nam, new Date().getMilliseconds());
    },
    hideLoader: function(nam, hiddenFrom) {
        if (!nam || nam == 'force') {
            if(this.processes.length)
            {
                console.log('Processes in progress => '+ this.processes.join(','));
                if(hiddenFrom)
                {
                    console.log('hidden from => '+ hiddenFrom);
                }
            }
            this.processes = [];
            if (!nam)
                console.trace();
            else if (nam != 'force')
            {
                console.log("Force hidden from " + hiddenFrom);
            }
            server_wait_loader.hide();
            server_wait_loader.shown = 0;
        }
        if (this.processes.length == 0) {
            loader_last_shown = undefined;
            clearTimeout(this.loadingTimeOut);
            //console.log("Already removed "+nam);
            return;
        }
        var found = false;
        for (var i = this.processes.length - 1; i >= 0; i--) {
            if (this.processes[i] == nam) {
                found = true;
                this.processes.splice(i, 1);
                break;
            }
        }
        if (found) {
            if(site_config.log_loading)
            {
                console.log('Loaded '+ nam + ' '+window['dt_functions'].now());
            }
        } else {
            console.log(nam + " not found");
        }
        if (this.processes.length == 0) {
            server_wait_loader.hide();
            loader_last_shown = undefined;
        }
        else{
            var loading_text = 'Loading '+this.processes.join(',');             
            server_wait_loader.find('.text strong').html(loading_text);
        }
        //console.log(nam, new Date().getMilliseconds());
    },
    change_cursor: function() {
        if (document.documentElement.style.cursor == '') {
            var myCanvas = document.getElementById("cursor_canvas");
            var ctx = myCanvas.getContext("2d");
            ctx.beginPath();
            ctx.arc(10, 10, 10, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();

            var url = myCanvas.toDataURL();
            url = 'url(' + url + ') , auto';
            document.documentElement.style.cursor = url;
            $('*').css('cursor', url);
        } else {
            $('*').css('cursor', '');

        }
    },
    togglerelated: function(selector) {
        $(selector).toggle();
    },
    get_trace : function(skip){
        var res = '';
        var obj = {};
        Error.captureStackTrace(obj);
        var trace = obj.stack.split('\n');
        for (var i in trace){
            if(i == 0)
            {
                continue;
            }
            if(i == 1 && skip)
            {
                continue;
            }
            if(trace[i].indexOf('DocumentComponent.push') > - 1
            ||  trace[i].indexOf('HTMLDocument.dispatch')> -1
            || trace[i].indexOf('ZoneDelegate.push')> -1)
            {
                break;
            }
            // var index = trace[i].indexOf('/assets');

            res += '\n\n'+ trace[i];//.substr(index+8);
        }
        console.log(res);
    }
};

(function(){
    $('body').click(function(event){
        if($(event.target).closest('.main-nav-header [data-toggle="sidebar"]').length)
        {
            $('body.user').toggleClass('sidenav-toggled');            
        }
        else{
            $('body.user').addClass('sidenav-toggled');
        }
    });

    $("body").on("click", ".top-search-btn", function() {
        if($(this).hasClass('user'))
        {
            $(".serach-input")
            .toggleClass("active")
            .focus();
            $(".btn-search").toggleClass("animate");
            $(".serach-input").val("");
        }
    });
})()

function addMainEventListeners() {
    window.addEventListener("dragover",function(e){
        e = e || event;
        e.preventDefault();
    },false);
    window.addEventListener("drop",function(e){
        e = e || event;
        e.preventDefault();
    },false);

    $('body').on('click', '.btnclosemodel', function() {
        $(this)
            .closest(".modal")
            .modal("hide");
    });
    $('body').on('hidden.bs.modal', '.modal', function() {
        $('body').removeClass('modal-open');
    });

    $(document).on('mousedown', function(e){
        if($('.popover.show').length){
            if(!$(e.target).closest('.bdp-input').length && !$(e.target).closest('.popover.show').length){
                var shown_popover_id = $('.popover.show').attr('id');
                $('.bdp-input[aria-describedby="'+shown_popover_id+'"]:first').click();
            }
        }
    });

    $(document).on("mouseup touchend keyup", function(e) {        
        if(!(dn_current_site_user && dn_current_site_user.cookie && dn_current_site_user.cookie.token))
        {
            return
        }
        refreshSession();
        if(!window['auth_js'].is_public_route())
        {
            localStorage.setItem('last_activity', Date());
        }
        if(loader_last_shown)
        {
            if(new Date() - loader_last_shown > 2000)
            {
                site_functions.hideLoader('force','');
            }
        }
        
        var target = e.target;
        var showbtn = $(target).closest('.showmouseawaybutton');
        if (showbtn && showbtn.length > 0) {
            return;
        }
        else
        {
            var shownpanel = $(target).closest('.hidemouseaway');
            if (shownpanel && shownpanel.length > 0)
                return;
            else {
                $('.hidemouseaway').hide();
            }
        }
    });
}


var public_methods = {
    'authsignup': {
        'AuthUser': {
            'login_user': 1
        }
    }
}

window.addEventListener('message', function receiveMessage(evt) {
    if (evt.origin === 'http://my.iframe.org') {
        alert("got message: " + evt.data);
    }

    if (evt.data.action) {
        let {
            id,
            model,
            action
        } = evt.data;
        // this.console.log(evt.data);
        var redirect_url = '';
        if (action === 'change' || action === 'add') {
            if (action === 'add')
            {
                id = 'new';
            }
            switch (model) {
                case 'event':
                    redirect_url = `/#/meeting/${id}`;
                    break;
                case 'news':
                    redirect_url = `/#/`;
                    break;
                case 'committee':
                    redirect_url = `/#/committees/${id}`;
                    break;
                case 'voting':
                    redirect_url = `/#/voting/${id}`;
                    break;
                case 'survey':
                    redirect_url = `/#/survey/${id}`;
                    break;
                case 'profile':
                    redirect_url = `/#/profile/${id}`;
                    break;
                case 'folder':
                    redirect_url = `/#/resource/${id}`;
                    break;
                case 'signdoc':
                    redirect_url = `/#/signdoc/${id}`;
                    break;
                case 'signaturedoc':
                    redirect_url = `/#/signdoc/${id}`;
                    break;
            }
        } else if(action == 'survey_submit')
        {
            switch(model)
            {
                case 'survey':
                    redirect_url = `/#/survey/${id}/results`;
            }
        } else {
            // this.console.log(model, action, evt);
            switch (model) {
                case 'event':
                        redirect_url = `/#/meetings/upcoming`;
                        break;
                case 'committee':
                        redirect_url = `/#/committees`;
                        break;
                case 'voting':
                        redirect_url = `/#/votings`;
                        break;
                case 'survey':
                        redirect_url = `/#/surveys`;
                        break;
                case 'profile':
                    redirect_url = `/#/profiles`;
                    break;
                case 'folder':
                    redirect_url = `/#/resources`;
                    break;
                case 'signdoc':
                    if(action == 'add')
                        redirect_url = `/#/signdoc/new`;
                    else
                        redirect_url = `/#/signdocs`;
                    break;
                case 'signaturedoc':
                    if(action == 'add')
                        redirect_url = `/#/signdoc/new`;
                    else
                        redirect_url = `/#/signdocs`;
                    break;
            }
        }
        // console.log(redirect_url, 233);
        if(redirect_url)
        {
            window.location = redirect_url;
        }
    }

}, false);


function refreshSession() {
    if(is_local_host)
    {
        //return;
    }
    if(time_out_session)
    {
        clearTimeout(time_out_session);
    }
    time_out_session = setTimeout(function() {
        site_functions.go_to_login();
    }, session_time_limit);
}

function check_if_touch_device() {    
    if(location_obj().toString().indexOf('localhost') > -1)
    {
        is_local_host = true;
    }
    if (location_obj().hash) {
        window['pathname'] = location_obj().hash.substr(1, location_obj().hash.length);
    } else {
        window['pathname'] = location_obj().toString().replace(origin_now(), '');
    }
    try
    {
        document.createEvent("TouchEvent");
        is_mobile_device = true;
        window['is_mobile_device'] = 1;
    }
    catch(e)
    {
        return false;
    }
}
$(function(){
    if($('body').hasClass('user'))
    {
        localStorage.setItem('last_activity', Date());
    }
})
window['current_user'] = dn_current_site_user;
window["functions"] = site_functions;
window['loader'] = server_wait_loader = $('#server-wait');
if(location_now().indexOf('/login') == -1)
{
    site_functions.showLoader('Site Resources');
}
// console.log(54343);
check_if_touch_device();
addMainEventListeners();
dn_current_site_user.initUserDataFromCookie();
refreshSession();
