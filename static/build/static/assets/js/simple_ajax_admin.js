function dn_rpc_object(options) {
    var api_url = options.url;
    if(!api_url)
    {
        api_url = '/rest/secure';
    }
    var server_base_url = window['server_url'];
    var req_url = server_base_url + api_url;
    if (!options.data) {
        console.log('No data and arguments for request ',options);
        return;
    }
    var input_data = options.data;    
    if (input_data.no_loader)
        options.no_loader = 1;

    var user_cookie = localStorage.getItem('user');
    if (user_cookie)
    {
        user_cookie = JSON.parse(user_cookie);
    }    
    options.no_loader = 1;    
    if(user_cookie)
    {
        input_data["auth_token"] = user_cookie.token;
    }
    
    var args_data = {input_data : JSON.stringify(input_data)};
    options.headers = {
        
    }
    if(user_cookie && user_cookie.token)
    {
        options.headers ['Authorization'] = 'Token '+user_cookie.token;
    }
    else if(api_url.endsWith('/secure'))
    {
        console.log(user_cookie, ' Invalid token for', input_data.args);        
        return;
    }

    options.data = args_data;
    options.dataType = 'json';
    if(!options.type)
    {
        if(req_url.indexOf('localhost')> -1)
        {
            if(input_data.args && input_data.args.post)
            {
                options.type = 'POST';
            }
            else
            {            
                options.type = 'GET';
            }
        }
        else
        {
            options.type = 'POST';
        }
    }
    
    //options.contentType = "application/json; charset=utf-8";    

    options.url = req_url;
    options.timeout = 30000;
    var loading_text = 'Data From Server'

    var url_with_params = 'Nothing';
    options.beforeSend = function(a, b) {
        url_with_params = b.url.toString();
        if(options.trace)
        {
            if(api_url == '/rest/secure')
            {
                url_with_params = url_with_params.replace('rest/secure','rest/secure1');
            }
            if(url_with_params.length < 1500)
            {
                console.log(url_with_params, input_data.args);    
            }
            else{
                console.log(input_data.args);
            }
        }
        if (!options.no_loader)
        {
            if(input_data.args){
                loading_text = input_data.args.model;
                if(is_localhost)
                {
                    loading_text += "."+input_data.args.method;
                }
            }
            site_functions.showLoader(loading_text);
        }
        if (options.type == 'post')
            url_with_params = options;
    };

    options.success = function(response) {
        var result = false;
        if (!response) {
            console.log("Undefined response", url_with_params);            
        } else if (response.data) {
            response = response.data;
            if (options.onSuccess) {
                try{
                    options.onSuccess(response);
                }
                catch(er)
                {
                    console.log(response, er);
                }
            }
        }
        else {
            if(!response.error)
            {
                response.error = response;
            }            

            handleError(response);
        }
    };
    options.complete = function() {
        if (options.onComplete)
            options.onComplete();
        if (!options.no_loader)
            site_functions.hideLoader(loading_text);        
    };
    options.error = function(err) {
        console.log('status '+err.status);
        if(err.status == 0)
        {
            err = 'Could not connect to server '+ server_base_url;
            if(window.navigator.onLine)
            {
                err += ' because no internet connection or server unavailble';
            }
            else
            {
                err += ' because server unavailble';
            }
            console.log(err);
            return;
        }
        if(err.status == 404)
        {
            er = api_url + ' unavailable at '+ server_base_url;
            console.log(err);
            return;
        }
        if(err.responseText == '{"detail":"Invalid token."}' || 
            err.responseText == '{"detail":"Authentication credentials were not provided."}')
        {
            console.log(input_data.args.method + ' needs login to be accessed');            
            return;
        }
        else
        {
            if (err.statusText =='OK')
            {                            
                err = {
                    error: err.responseText
                }     
                handleError(err);       
            }
            else{
                console.log(err, 'Api failed', args);
            }
        }
    };


    function handleError(response)
    {
        if(response.error && response.error.data)
        {
            console.log(response.error.data);
            response.error = response.error.message;
        }
        if (response.error.indexOf('oken not valid') > -1 || response.error.indexOf('please login') > -1) {                        
            console.log('Token expired, please login again '+ options.url);            
            return;
        } else if (response.error.indexOf('not allowed to access') > -1) {
            bootbox.alert("Contact admin for permissions" + response.error);
        } else {                                
            if(response.error.indexOf('Unauthorized') > -1)
            {
                console.log('Unauthorized request to access resources')
                return;
            }
            else if(options.onError) {
                try{
                    options.onError(response.error);
                }
                catch(er)
                {
                    console.log(response.error, er);
                }                        
            }                
        }
        if(!options.trace)
        {
            console.log(input_data.args);
            if(options.type == 'GET' && url_with_params.length < 1500)
            {
                console.log(url_with_params);
            }
        }
        
        response.error = response.error.replace(/<br\/>/g, "\n");
        console.log(response.error);
    }
    $.ajax(options);
}
$(function(){
    var container = $('#container');
    if(container.length > 0)
    {
        if(self != top)
        {
            container.css('overflow-x', 'hidden');    
        }
    }    
});
window['dn_rpc_object'] = dn_rpc_object;
