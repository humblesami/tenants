$(function(){
    var meeting_id = $('.field-meeting select').val();
    if(meeting_id)
    {
        $('.form-row.field-send_to_all').show();
    }
    else{
        $('.form-row.field-send_to_all').hide();
    }
    $('.field-meeting select').on('change', function(){
        meeting_id = $(this).val();
        if (meeting_id)
        {
            $('.form-row.field-send_to_all').show();
        }
        else
        {
            $('.form-row.field-send_to_all select').val('false');
            $('.form-row.field-send_to_all').hide();
        }
    });
    // open('/home/sami/django/jangomeet'+old_file.attachment.url)

    // base64.b64encode(open('/home/sami/django/jangomeet' + old_file.attachment.url, "rb").read())
    // self.binary_data.split(';base64,')[1]
    // old_file.attachment.file.file
    if($('#id_attachment').length)
    {
        // $('#id_attachment').attr('multiple','multiple');
        apply_drag_drop($('#id_attachment'));
        $('.form-row.field-attachment').show();
        $('.form-row.field-respondents').show();
    }
});

