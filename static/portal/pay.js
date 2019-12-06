$(function(){
//    $("#comapny_name" ).blur(function(e) {
//        e.preventDefault();
//        if($("#comapny_name" ).val() == ''){
//            return
//        }
//        $("#comapny_name_error").hide();
//        var name = $("#comapny_name" ).val();
//        var params = { 'name' : name };
//        window['js_utils']['ajax']({
//            url:'/subscriptions/check-name',
//            data:params,
//            dataType: 'json',
//            success:function(data){
//                if(data >= 1){
//                    $("#comapny_name_error").html("Name Already Exist");
//                    $("#comapny_name_error").show();
//                }
//
//                console.log(data,'ok');
//            },
//            error:function(e){
//                console.log(e, 'err in ajax');
//            }
//        });
//    });

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
//        if($("#comapny_name").val() == '' || $("#email").val() == ''){
//            if($("#comapny_name").val() == ''){
//                $("#comapny_name_error").html("Add Name First");
//                $("#comapny_name_error").show();
//            }
//            if($("#email").val() == ''){
//                $("#email_error").show();
//            }
//            return
//        }
//        $("#email_error").hide();
//        $("#comapny_name_error").hide();
//        var name = $("#comapny_name").val();
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
//                    $("#comapny_name_error").html("Name Already Occupied");
//                    $("#comapny_name_error").show();
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

