    
    $(function(){

        $('.new-password').keyup(function() {
            new_password = $('.new-password').val(),
            confirm_new_password = $('.confirm-password').val(),
            all_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@~`!@#$%^&*()_=+\\';:"\/?>.<,-])(?=.{8,})/,
            lower_regex = /^(?=.*[a-z])/,
            uper_regex = /^(?=.*[A-Z])/,
            numeric_regex = /^(?=.*[0-9])/,
            special_regex = /^(?=.*[@~`!@#$%^&*()_=+\\';:"\/?>.<,-])/,
            min_length_regex = /^(?=.{8,})/;
            if(lower_regex.test(new_password))
            {
                $('.lower-case-rule').addClass('valid-password');
            }
            else
            {
                $('.lower-case-rule').removeClass('valid-password');
            }
            if(uper_regex.test(new_password))
            {
                $('.uper-case-rule').addClass('valid-password');
            }
            else
            {
                $('.uper-case-rule').removeClass('valid-password');
            }
            if(numeric_regex.test(new_password))
            {
                $('.numeric-rule').addClass('valid-password');
            }
            else
            {
                $('.numeric-rule').removeClass('valid-password');
            }
            if(special_regex.test(new_password))
            {
                $('.special-char-rule').addClass('valid-password');
            }
            else
            {
                $('.special-char-rule').removeClass('valid-password');
            }
            if(min_length_regex.test(new_password))
            {
                $('.max-8-char-rule').addClass('valid-password');
            }
            else
            {
                $('.max-8-char-rule').removeClass('valid-password');
            }
            if(all_regex.test(new_password) && new_password == confirm_new_password)
            {
                $('.submit-btn').removeAttr('disabled')
            }
            else
            {
                $('.submit-btn').attr('disabled','disabled')
            }
        });
        
        $('.confirm-password').keyup(function() {
            new_password = $('.new-password').val(),
            confirm_new_password = $('.confirm-password').val(),
            all_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@~`!@#$%^&*()_=+\\';:"\/?>.<,-])(?=.{8,})/;
            
            if(all_regex.test(new_password) && new_password == confirm_new_password)
            {
                $('.submit-btn').removeAttr('disabled');
                $('.password-match-rule').addClass('valid-password');
            }
            else
            {
                $('.submit-btn').attr('disabled','disabled');
                $('.password-match-rule').removeClass('valid-password');
            }
        });
        
        
        $('.pass_show .ptxt').click(function() {
            $(this).text($(this).text() == "Show" ? "Hide" : "Show");
            $(this).prev().attr('type', function(index, attr) {
                return attr == 'password' ? 'text' : 'password';
            });
        });

        var token_str = window.location.toString().split('/');
        token_str = token_str[token_str.length - 1];
        $('#token').val(token_str)
        $('button.submit-btn').click(function(){
            $('.feedback').html('');
            var input_data = {
                args:{
                    app: 'authsignup',
                    model: 'AuthUser',
                    method: 'set_user_password',
                },
                params: {
                    password: $('#password').val(),
                    token: $('#token').val(),
                }
            }
            var options = {
                url: '/rest/public',
                data: input_data
            }
            options.onSuccess = function(data){
                if(data == 'done'){
                    window.location = site_config.server_base_url + '/user/login';
                }
                else
                {
                    $('.feedback').html(data);
                }
            };
            options.type = 'get';
            options.onError = function(a,b,c,d){
                console.log(a,b,c,d);
                $('.feedback').html(a);
            };
            options.onComplete = function(data){
                
            };
            window['dn_rpc_object'](options);
        })
    })
