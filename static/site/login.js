//http://localhost:8001/accounts/login
//http://localhost:8001/accounts/login
$(function(){    
    var next_url = window['js_utils']['get_param']('next') || '/';
    $('#next_url').val(next_url);
    console.log(next_url);
//    $('#login-form').submit(function(e){
//        e.preventDefault();
//        var options = {
//            url:'/authenticate',
//            data:{
//                login: $('#username').val(),
//                password: $('#password').val(),
//                next_url: $('#next_url').val()
//            },
//            success:function(data){
//                if(data == 'done')
//                {
//                    window.location = next_url || '/';
//                }
//                else{
//                    $('#feedback').html(data);
//                }
//            },
//            error: function(e)
//            {
//                console.log('error', e);
//            }
//        }
//        console.log(options);
//        window['js_utils']['ajax'](options);
//    })
})