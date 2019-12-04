$(function(){

    
      $("#comapny_name" ).blur(function(e) {
        e.preventDefault();
        if($("#comapny_name" ).val() == ''){
            return
        }
        $("#comapny_name_error").hide();
        var name = $("#comapny_name" ).val();
        var params = { 'name' : name };
        $.ajax({
            url:'/stripe/checkname',
            data:params,
            dataType: 'json',
            success:function(data){
                console.log(data, 'data in ajax');
                if(data == 'done'){
                    console.log(data, 'data in ajax');      
                }
            },
            error:function(e){
                console.log(e, 'err in ajax');
            }
        })

    });

    // $('.stripe-button-el').hide();
    $('#btn_add_request').click(function(e){
        e.preventDefault();
        if($("#comapny_name").val() == '' || $("#email").val() == ''){
            if($("#comapny_name").val() == ''){
                $("#comapny_name_error").show();
            }
            if($("#email").val() == ''){
                $("#email_error").show();
            }
            return
        }
        $("#email_error").hide();
        $("#comapny_name_error").hide();
        var name = $("#comapny_name").val();
        var email = $("#email").val();
        var params = { 'name' : name, 'email' : email}
        $.ajax({
            url:'/stripe/addrequest',
            data:params,
            dataType: 'json',
            success:function(data){
                console.log(data, 'data in ajax');
                if(data.is == 'done')
                {
                    $('.stripe-button-el').click();
                }
            },
            error:function(e){
                console.log(e, 'err in ajax');
            }
        });
        //$('.stripe-button-el').click();
    });

})
