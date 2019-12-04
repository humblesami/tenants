$(function(){
    // $('.stripe-button-el').hide();
    $('#btn_add_request').click(function(e){
        e.preventDefault();
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


    $("#comapny_name" ).blur(function(e) {
        e.preventDefault();
        var name = $("#comapny_name" ).val();
        var param = { 'name' : name }
        $.ajax({

            ulr: '/stripe/checkname',
            data: param,
            dataType: 'json',
            success:function(data){
                console.log(data);
                if(data == 'done'){
                    console.log(data);
                }else{
                    console.log(data);
                }
            },
            error:function(e){
                console.log(e, "Error ");
            }

        })

    });
})
