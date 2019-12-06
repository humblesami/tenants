$(function(){
       $("#password, #confirm_password" ).keyup(function(e) {
            var password = $('#password').val();
            var confirm_password = $('#confirm_password').val();
            if(password && confirm_password)
            {
                if(password != confirm_password)
                {
                    $('#btn_add_request').attr('disabled', 'disabled');
                    $('#confirm_password_error').show();
                }
                else{
                    $('#btn_add_request').removeAttr('disabled');
                    $('#confirm_password_error').hide();
                }
            }
       });
   $("#company_name" ).blur(function(e) {
       e.preventDefault();
       if($("#company_name" ).val() == ''){
           return
       }
       $("#company_name_error").hide();
       var name = $("#company_name" ).val();

       var params = { 'name' : name };
       console.log(params)
       window['js_utils']['ajax']({
           url:'/subscriptions/check-name',
           data:params,
           dataType: 'json',
           error:function(data){
            if(data != "done"){
                $("#company_name_error").html("User Already Exist");
                $("#company_name_error").show();
            }
           }
       });
   });

//    $("#email").blur(function(e){
//        e.preventDefault();
//        var email = $("#email").val();
//        var check = ValidateEmail(email)
//        if(check){
//            $("#email_error").html("")
//            $("#email_error").hide();
//        }else{
//            $("#email_error").html("Please Enter a valid Email Address")
//            $("#email_error").show();
//        }
//    });



//    $('#btn_add_request').click(function(e){
//        e.preventDefault();
//        if($("#company_name").val() == '' || $("#email").val() == ''){
//            if($("#company_name").val() == ''){
//                $("#company_name_error").html("Add Name First");
//                $("#company_name_error").show();
//            }
//            if($("#email").val() == ''){
//                $("#email_error").show();
//            }
//            return
//        }
//        $("#email_error").hide();
//        $("#company_name_error").hide();
//        var name = $("#company_name").val();
//        var email = $("#email").val();
//        var params = { 'name' : name, 'email' : email}
//        window['js_utils']['ajax']({
//            url:'/subscriptions/save-request',
//            data:params,
//            dataType: 'json',
//            success:function(data){
//                $('.stripe-button-el').click();
//            },
//            error : function(e){
//                if(e == "User already Exist"){
//                    $("#company_name_error").html("Name Already Occupied");
//                    $("#company_name_error").show();
//                }
//                console.log(e,"Error in ajax")
//            }
//        });
//    });

    function ValidateEmail(mail) 
    {
        if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail))
        {
            return (true)
        }
            return (false)
    }
})

