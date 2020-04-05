$('form:first').submit(function(e){
    e.preventDefault();
    var input_data = {};
    $('.form-controls input').each(function (i, el) {
        input_data[el.name] = el.value;
    });
    
    
    var url = '/pull';
    if($('input[name="message"]').val())
    {
        url = '/push';
    }
    var options = {
        url: url,
        beforeSend:function(){
            $('button').prop('disabled', true);
        },
        data:input_data,
        success:function (data) {
            console.log(data);
        },
        error:function (er) {
            console.log(er);
        },
        complete:function(){
            $('button').prop('disabled', false);
        }
    };
    $.ajax(options);
});
