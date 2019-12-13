$(function(){
    if(!$('#next_url').val())
    {
        var next_url = window['js_utils']['get_param']('next') || '/';
        $('#next_url').val(next_url);
    }
    else{
        next_url = $('#next_url').val();
    }
})