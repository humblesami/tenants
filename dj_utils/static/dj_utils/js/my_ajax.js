class AJAxForm{
    constructor(){
        this.form_options = undefined;
        this.form_js = undefined;
        this.form_jq = undefined;
        this.poster_btn = undefined;
    }
    bind_form(selector){
        let form = $(selector);
        this.form_jq = form;
        this.form_js = form[0];
        let poster_btn = this.poster_btn = form.find('[type="submit"]:first');
        let submit_url = form.attr('action');
        let obj_this = this;
        let form_options = this.form_options = {
            success : function(response)
            {
                obj_this.success(response);
            },
            complete : function(response)
            {
                obj_this.complete(response);
            },
            error : function(response)
            {
                obj_this.error(response);
            }
        };
        if(!submit_url){
            submit_url = form_options.url;
        }
        if(!form_options.url){
            form_options.url = form.attr('action');
        }
        form_options.type = $(form).attr('method') || 'GET';
        form_options.dataType = 'JSON';
        form.submit(function(e){
            e.preventDefault();
            if(!form.find(".error-message").length){
                form.prepend('<h5 class="error-message"></h5>');
            }
            form.find('.error-message:first').hide();
            poster_btn.attr('disabled', 'disabled');
            form.ajaxSubmit(form_options);
        });
    }
    success(data){
        let message = 'Invalid status response from API';
        let form_options = this.form_options;
        let form_js = this.form_js;
        let obj_this = this;
        console.log('super success', data);
        if(data && data.status){
            if(data.status == 'success'){
                form_js.reset();
            }
            else{
                if(data.status == 'error' && data.message)
                {
                    message = data.message;
                    obj_this.on_error(message);
                }
            }
        }
        else{
            obj_this.on_error(data);
        }
        return data;
    }
    on_error(er){
        form.find('.error:first').html(er+' in '+submit_url).show();
    }
    error(data){
        let form_options = this.form_options;
        let message = '';
        let obj_this = this;
        if(data && data.responseJSON && data.responseJSON.message)
        {
            message = data.responseJSON.message;
        }
        else{
            message = $(data.responseText);
            message = ajax92.parseMessage(message, 'django');
        }
        obj_this.on_error(message);
    }
    complete(){
        let form_options = this.form_options;
        this.poster_btn.removeAttr('disabled');
        if(form_options.on_complete){
            form_options.on_complete();
        }
        form.find('textarea:visible, input:visible, select:visible').first().focus();
    }
}

var ajax92 = {
    http: function(ajax_options){
        if(!ajax_options){
            ajax_options = {}
        }
        ajax_options.dataType = 'JSON';
        let submit_url = ajax_options.url;
        ajax_options.success = function(data){
            let message = 'Invalid status response from API';
            if(data && data.status){
                if(data.status == 'success'){
                    if(ajax_options.on_success)
                    {
                        ajax_options.on_success(data.data);
                    }
                    else{
                        console.log(data);
                    }
                    return;
                }
                else{
                    if(data.detail)
                    {
                        console.log(data.detail);
                    }
                    if(data.status == 'error' && data.message)
                    {
                        message = data.message;
                    }
                }
            }
            if(ajax_options.on_error)
            {
                ajax_options.on_error({message: message});
            }
            else{
                console.log(data.detail);
            }
        }

        ajax_options.error = function(data){
            let message = '';
            if(data && data.responseJSON && data.responseJSON.message)
            {
                message = data.responseJSON.message;
            }
            else{
                message = $(data.responseText);
                message = ajax92.parseMessage(message, 'django');
            }
            if(ajax_options.on_error)
            {
                ajax_options.on_error({message: message});
            }
            else{
                console.log(message);
            }
        }

        ajax_options.complete = function(){
            if(ajax_options.on_complete){
                ajax_options.on_complete();
            }
        }
        $.ajax(ajax_options);
    },
    parseMessage: function(arr, framework){
        let error_message = 'Error not parsed';
        switch(framework){
            case 'django':
                for(let el of arr){
                    if(el.id == 'summary')
                    {
                        if(el.childNodes.length>1)
                        {
                            el.innerHTML = el.childNodes[0].outerHTML + el.childNodes[1].outerHTML;
                        }
                        error_message = el.outerHTML;
                    }
                }
            break;
        }
        return error_message;
    }
}
$(function(){
    $('textarea:visible, input:visible, select:visible').first().focus();
});