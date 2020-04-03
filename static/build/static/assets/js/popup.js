
function init_popup(config) {
    var modal_obj = $('#appModal');
    modal_obj.find('.modal-header .title').html('');
    modal_obj.find('.modal-body').html('');
    modal_obj.find('.modal-footer button:not(#save-sig):not(#close-btn)').remove();
    var save_btn = modal_obj.find('#save-sig');
    if(!config.no_save)
    {
        save_btn.off('click').show();
        save_btn.click(function(){        
            if (config.on_save)
            {
                config.on_save();
            }
            if(config.hide_on_save || config.hide)
            {
                modal_obj.modal('hide');
            }
        });
    }
    else{
        save_btn.hide();
    }
    modal_obj.find('#close-btn').off('click');
    modal_obj.find('#close-btn').click(function(){
        if (config.on_close)
        {
            config.on_close();
        }
        modal_obj.modal('hide');
    });
    if(config.on_load)
    {
        config.on_load();
        if(modal_obj.find('.modal-header:first').text() == '')
        {
            modal_obj.find('.modal-header .title:first').html('Dialog')
        }
    }
    if(config.title)
    {
        modal_obj.find('.modal-header .title:first').html(config.title);
    }
    else{
        if(!modal_obj.find('.modal-header .title:first').html())
        {
            modal_obj.find('.modal-header .title:first').html('Dialog');
        }
    }
    modal_obj.modal('show');
};
window['init_popup'] = init_popup;
$(function(){
    $(document).on('click', 'label.overflow-hidden', function(){
        var c_label = this;        
        var label_show = {
            on_load: function(){
                $('#appModal .modal-body').html(c_label.innerHTML);
            }
        }
        init_popup(label_show);
    });
    $('#appModal').on('shown.bs.modal', function(){
        $(this).find('input:visible:first').focus();
    })
})
