$(function(){
    $('#login-form').submit(function(e){
        e.preventDefault();
        $.ajax({
            url:'/authenticate',
            data:{
                login: $('#login').val(),
                password: $('#password').val(),
            },
            success:function(data){
                if(data == 'done')
                {
                    window.location = '/';
                }
                else{
                    $('#feedback').html(data);
                }
            },
            error: function(e)
            {
                console.log('error', e);
            }            
        })
    })
})