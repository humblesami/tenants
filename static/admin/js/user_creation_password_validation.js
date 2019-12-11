$(document).ready(function(){
    console.log('document loaded');
    $('#id_password1,#id_password2').blur(on_pasaword_change);
    $('#id_password1,#id_password2').keyup(on_pasaword_change);

    function on_pasaword_change(){
        if(this.id == "id_password1")
        {
            if(!$('#id_password2').val())
            {
                return;
            }
        }
        if($('#id_password1').val() == $('#id_password2').val()){            
            $("#eMessage").remove();
            $('.submit-row input').attr('disabled',false);
        }else{            
            $("#eMessage").remove();
            $(this).after('<div id="eMessage"><label style="color:red" for="name">Password Not Match</label></div>');
            $('.submit-row input').attr('disabled',true);
        }
    }
})