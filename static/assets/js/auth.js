(function(){    
    var wl = window.location;
    var wl_str = wl.toString();
    window['auth_js'] = {
        add_public_class: add_public_class,
        add_user_class: add_user_class,
        is_public_route: is_public_route
    } 
    function add_public_class(){        
        $('body').removeClass('user').addClass('public');
    }
    function add_user_class(){
        $('body').removeClass('public').addClass('user');
    }
    function verifyUserToken() {
        if(is_public_route())
        {
            return;
        }
        var user_cookie = localStorage.getItem('user');
        if (user_cookie) {
            var last_activity = localStorage.getItem('last_activity');
            if(!last_activity)
            {
                go_to_login();
                return;
            }
            else{
                var time_now = new Date();
                last_activity = new Date(last_activity);
                var diff = (time_now - last_activity) /1000;
                // console.log('Last activity', diff, window.location.hostname, Date());
                if(window.location.hostname != 'localhost' && diff > 30)
                {
                    go_to_login();
                    return;
                }
            }
            user_cookie = JSON.parse(user_cookie);
            if (user_cookie.token) {
                var error = undefined;
                var ajax_options = {
                    url: site_config.server_base_url + '/user/verify-token',
                    async: false,
                    headers: {
                        Authorization:
                        'Token '+user_cookie.token
                    },
                    error: function(er){
                        if(er.responseJSON)
                        {
                            er = er.responseJSON.detail;
                        }
                        error = er;
                        console.log(er);
                    },
                    complete:function(){
                        // console.log(error, public_route);
                        if(!error)
                        {
                            localStorage.setItem('last_activity', Date());
                            add_user_class();
                        }
                        else{
                            go_to_login();
                            return;
                        }
                    }
                }
                $.ajax(ajax_options);
            }
            else{
                go_to_login();
            }
        }
        else
        {
            go_to_login();
        }
    }
    function get_cpath_name() {
        var wl = window.location;
        if(wl.toString().indexOf('localhost') > -1)
        {
            is_local_host = true;
        }
        if (wl.hash) {
            window['pathname'] = wl.hash.substr(1, wl.hash.length);
        } else {
            window['pathname'] = wl.toString().replace(wl.origin, '');
        }
        return window['pathname'];
    }
    function is_public_route(url){
        if(!url)
        {
            url = get_cpath_name();
        }
        let public_routes = [
            '/user/login',
            '/user/forgot-password',
            '/user/reset-password',
            '/login','/forgot-password',
            '/logout','/reset-password',
            '/token-sign-doc',
            '/thanks',
            '/feedback',
            '/public-voting/',
            '/public-meeting/',
        ];
        for (var i in public_routes)
        {
            if (url.startsWith(public_routes[i]))
            {
                localStorage.removeItem('user');
                add_public_class();
                return true;
            }
        }
        return false;
    }
    window['is_public_route'] = is_public_route;
    function go_to_login() {
        localStorage.removeItem('user');
        add_public_class()
        if(!wl_str.endsWith('login'))
        {
            if(wl_str.indexOf('4200') == -1)
            {
                window.location = '/user/login';
            }
            else{
                window.location = '/#/login';
            }
        }
    }
    verifyUserToken();
})()