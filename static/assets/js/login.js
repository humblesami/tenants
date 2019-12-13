(function(){
    $('.Login-form-wrapper img').each(function(i, el){
        $(el).attr('src', $(el).attr('src_url'));
    });

    $('.login-form:first input').keyup(function(){
        $(this).find('.login-feedback').html('');
    });
    var form  = $('.login-form:first');
    form.submit(function(e){
        var logged_in = false;
        e.preventDefault();
        form.find('button[type="submit"]:first').attr('disabled', 'disabled');
        $('#server-wait').show();
        var input_data = {
            args:{
                app: 'authsignup',
                model: 'AuthUser',
                method: 'login_user',
            },
            params: {
                login: form.find('#username').val(),
                password: form.find('#password').val(),
            }
        }
        form.find('.login-feedback').html('');
        var options = {
            url: '/rest/public',
            data: input_data,
            show_loader: 1
        }
        $('#server-wait').show();
        options.onSuccess = function(data){
            logged_in = true;
            $('#server-wait').show();
            form.find('button[type="submit"]:first').removeAttr('disabled');
            // console.log(data);
            if(data.uuid && data.auth_type && data.status)
            {
                data = JSON.stringify(data);
                localStorage.setItem('auth_code_data', data);
                window.location = '/user/verify-auth-code';
            }
            else
            {
                data = JSON.stringify(data);
                localStorage.setItem('user', data);
                localStorage.setItem('last_activity', Date());
                window.location = "/";
            }
        };
        options.type = 'get';
        options.onError = function(data){
            form.find('button[type="submit"]:first').removeAttr('disabled');
            form.find('.login-feedback').html(data);
            $('#server-wait').hide();
        };
        options.onComplete = function(data){
            form.find('button[type="submit"]:first').removeAttr('disabled');
            if(logged_in)
            {
                $('#server-wait').show();
            }
        };
        window['dn_rpc_object'](options);
        $('#server-wait').show();
    });
    $('.Login-form-wrapper').css('over-flow', 'auto');
    $('.login-logo-image').show();
})()
