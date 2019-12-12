(function(){
    var js_utils = {
        get_param : function(p_name, url = window.location.toString()){
            const urlParams = new URLSearchParams(window.location.search);
            const myParam = urlParams.get(p_name);
            return myParam
        },
        ajax : function(options){
            // console.log(options);
            if(!options.type)
            {
                options.type = 'GET';
            }
            $.ajax({
                url: options.url,
                data:options.data,
                dataType: 'json',
                type: options.type,
                success:function(data){
                    try{
                        data = JSON.parse(data);
                    }
                    catch{

                    }
                    if(data.error)
                    {
                        // console.log(data.error);
                        if(options.error){
                            options.error(data.error);
                        }
                        return;
                    }
                    if(data.data){
                        data = data.data;
                    }
                    if(options.success)
                    {
                        options.success(data);
                    }
                },
                error:function(e){
                    var err_text = '';
                    console.log(e);
                    try{
                        var dom = $(e.responseText);
                        err_text = dom.text();
                    }
                    catch(er){
                        err_text = 'Unknown error';
                    }
                    if(options.error){
                        options.error(err_text);
                    }
                }
            });
        }
    }
    window['js_utils'] = js_utils;    
    // console.log(window['js_utils']);
})()