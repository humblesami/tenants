function dn_rpc_object(options) {
    var api_url = options.url;
    if(!api_url)
    {
        api_url = '/rest/secure';
    }
    var req_url = site_config.server_base_url + api_url;
    if (!options.data) {
        console.log('No data and arguments for request ',options);
        return;
    }
    console.log(site_config.server_base_url, req_url);
    var input_data = options.data;    
    if (input_data.no_loader)
        options.no_loader = 1;

    var ajax_user = window['current_user'];    

    //console.log(input_data);
    if (input_data.no_loader)
    {
        options.no_loader = 1;
    }
    if(ajax_user.cookie)
    {
        input_data["auth_token"] = ajax_user.cookie.token;
    }
    
    var args_data = {input_data : JSON.stringify(input_data)};
    options.headers = {
        
    }
    if(ajax_user.cookie && ajax_user.cookie.token)
    {
        options.headers ['Authorization'] = 'Token '+ajax_user.cookie.token;
    }
    else if(api_url.endsWith('/secure'))
    {        
        handle_authorization('Invalid acces to secure api');        
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
    var loading_text = 'Data From Server';
    var url_with_params = 'Nothing';
    options.beforeSend = function(a, b) {
        url_with_params = b.url.toString();
        if(site_config.trace_request || is_localhost)
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
            } else if(site_config.show_logs.indexOf('ajax_success')){
                // console.log(response);
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
        if (!options.show_loader && !options.no_loader)
            site_functions.hideLoader(loading_text);
    };
    options.error = function(err) {   
        console.log('status '+err.status);
        if(err.status == 0)
        {
            err = 'Could not connect to server '+site_config.server_base_url;
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
            er = api_url + ' unavailable at '+ site_config.server_base_url;
            console.log(err);
            return;
        }

        if(err.responseText == '{"detail":"Invalid token."}' || 
            err.responseText == '{"detail":"Authentication credentials were not provided."}')
        {
            console.log(input_data.args.method + ' needs login to be accessed');
            handle_authorization(err.responseText);
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
                console.log('Api failed to reach');
            }
        }
    };

    function handle_authorization(err){
        try{
            console.log(err);
            var is_admin = ajax_user.cookie.groups.find(function(item){
                return item.name == 'Admin';
            });
            if(!is_admin)
            {
                window['functions'].go_to_login();
            }
        }
        catch(err){
            window['functions'].go_to_login();
        }
        site_functions.hideLoader("ajax" + api_url);
    }


    function handleError(response)
    {        
        if(response.error && response.error.data)
        {
            console.log(response.error.data);
            response.error = response.error.message;
        }
        if(response.error){
            response.error = response.error.replace(/<br\/>/g, "\n");
            console.log(response.error);
        }
        response.error = response.error.replace(/[^0-9a-z _/\\]/gi, '')
        var report_str_index = response.error.indexOf('report_error_dev');        
        if(report_str_index > -1)
        {
            response.error = response.error.substr(0, report_str_index);
        }
        if(response.error.length > 200){            
            response.error = response.error.replace(/<br\/>/g, "\n");            
            response.error = response.error.substr(0, 200);
        }
        
        if (response.error.indexOf('oken not valid') > -1 || response.error.indexOf('please login') > -1) {                        
            bootbox.alert('Token expired, please login again '+ options.url);            
            handle_authorization();
            return;
        } else if (response.error.indexOf('not allowed to access') > -1) {
            bootbox.alert("Contact admin for permissions" + response.error);
        } else {                                
            if(response.error.indexOf('Unauthorized') > -1)
            {
                handle_authorization(response.error);
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
        // if(!site_config.trace_request)
        // {
        // console.log(input_data.args);
        if(options.type == 'GET' && url_with_params.length < 1500)
        {
            console.log(url_with_params);
        }
        // }            
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
