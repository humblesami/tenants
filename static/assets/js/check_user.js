(function(){
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
                return true;
            }
        }
        return false;
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
    }
    console.log(Date()+'-' + new Date().getMilliseconds());
})()