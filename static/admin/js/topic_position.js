function set_topic_position()
{
    $('.djn-dynamic-form-meetings-topic:not([data-is-initial=false]) .vIntegerField').each(function(i,el){
        $(el).val(i+1)
    })
}

$(document).ready(()=>{
    $('.field-position').hide();
    $('.submit-row input[type="submit"]').on('mousedown', ()=>{
        set_topic_position();
    });
    $('.submit-row input[type="submit"]').on('touchstart', ()=>{
        set_topic_position();
    });
});