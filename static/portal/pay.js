$(function(){
    $("#comapny_name" ).blur(function(e) {
        e.preventDefault();
        if($("#comapny_name" ).val() == ''){
            return
        }
        $("#comapny_name_error").hide();
        var name = $("#comapny_name" ).val();
        var params = { 'name' : name };
        window['ajax']({
            url:'/stripe/check-name',
            data:params,
            dataType: 'json',
            success:function(data){
                console.log('ok');
            },
            error:function(e){
                console.log(e, 'err in ajax');
            }
        });
    });

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
        window['ajax']({
            url:'/stripe/add-request',
            data:params,
            dataType: 'json',
            success:function(data){
                $('.stripe-button-el').click();
            }
        });
    });
})
