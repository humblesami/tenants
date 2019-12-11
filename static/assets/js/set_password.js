    (function(){
            $('.submit-btn').click(function(e){
                e.preventDefault();
                let arr = window.location.toString().split('/')
                let token = arr[arr.length-1]
                var input_data = {
                    args:{
                        app: 'authsignup',
                        model: 'AuthUser',
                        method: 'set_user_password',
                    },
                    params: {
                        password: $('.new-password').val(),
                        token: token,
                    }
                }
                var options = {
                    url: '/rest/public',
                    data: input_data
                }
                options.onSuccess = function(data){
                    window.location = '/user/login';
                };
                options.type = 'get';
                options.onError = function(data){
                };
                window['dn_rpc_object'](options);
            })
        })()
