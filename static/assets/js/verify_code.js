(function(){
    $('.login-form:first input').keyup(function(){
        $(this).find('.login-feedback').html('');
    });    
    var auth_code_data = localStorage.getItem('auth_code_data');
    try{
        auth_code_data = JSON.parse(auth_code_data);
    }
    catch(er){
        auth_code_data = {
            
        }
    }
    
    var auth_code_message = 'Please check your '+auth_code_data.auth_type+' to get latest verification code just received';
    $('.auth_code_message').html(auth_code_message);
    $('.login-form:first').submit(function(e){
        e.preventDefault();
        var form  = $(this);
        form.find('button[type="submit"]:first').attr('disabled', 'disabled');
        var input_data = {
            args:{
                app: 'authsignup',
                model: 'AuthUser',
                method: 'login_user',
            },
            params: {
                auth_code: form.find('#auth_code').val(),
                uuid: auth_code_data.uuid
            }
        }
        form.find('.login-feedback').html('');
        var options = {
            url: '/rest/public',
            data: input_data
        }
        options.onSuccess = function(data){
            form.find('button[type="submit"]:first').removeAttr('disabled');
            dn_current_site_user.onLogin(data);
            var return_url = new URL(window.location.toString());
            return_url = return_url.searchParams.get("next");
            console.log(return_url);
            if(return_url)
            {
                window.location = return_url;
            }
            else
            {
                window.location = "/";
            }
        };
        options.type = 'get';
        options.onError = function(data){
            form.find('button[type="submit"]:first').removeAttr('disabled');
            form.find('.login-feedback').html(data);
        };
        options.onComplete = function(data){
            console.log(4444);
            form.find('button[type="submit"]:first').removeAttr('disabled');
        };
        window['dn_rpc_object'](options);
    })
})()