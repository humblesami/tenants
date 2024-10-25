(function(){
    let modal = $('#single_popup');

    window.sam_modal = {
        jq_dom: modal,
        on_submit: function(){

        }
    };

    window.sam_modal.open = function(body=''){
        window.sam_modal.name
        modal.find('.body').html(body);
        modal.show();
    }

    window.sam_modal.close = function(){
        modal.hide();
    }

    window.sam_modal.csrf_token = modal.find('input[name="csrfmiddlewaretoken"]:first').val();
    modal.find('.btn.close').click(function() {
        window.sam_modal.close();
    });
    modal.find('.btn.submit').click(function() {
        window.sam_modal.on_submit();
    });
})();