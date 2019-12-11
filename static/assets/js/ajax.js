function ajax_request(options) {
    var server_base_url = window['server_url'];
    var req_url = options.url;
    options.dataType = 'json';
    // options.contentType = "application/json; charset=utf-8";
    options.timeout = 30000;

    var url_with_params = 'Nothing';
    options.beforeSend = function(a, b) {
        url_with_params = b.url.toString();
        if(options.trace)
        {
            if(url_with_params.length < 1500)
            {
                console.log(url_with_params, options.data);    
            }
            else{
                console.log(options.data);
            }
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
            err = req_url + ' unavailable';
            console.log(err);
            return;
        }
        if(err.responseText == '{"detail":"Invalid token."}' || 
            err.responseText == '{"detail":"Authentication credentials were not provided."}')
        {
            console.log(req_url + ' needs login to be accessed');            
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
                console.log(err, 'Api failed');
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
window['ajax_request'] = ajax_request;
