(function(){
    $(function(){
        var origin  = window.origin.toString();
        console.log(origin);
        var arr = origin.split('.');
        var cnt = 55;
        while(arr.length > 1 && cnt++ < 59)
        {
            let chunk = arr[0];
            if(chunk.indexOf('/') > -1)
            {
                var temp_ar = chunk.split('/');
                chunk = temp_ar[temp_ar.length - 1];
            }
            origin = origin.replace(chunk+'.', '');
            arr = origin.split('.');
        }
        console.log(origin);
        $('a.public_home_link').attr('href', origin);
    })

    window['ajax'] = function(options){
        $.ajax({
            url: options.url,
            data:options.data,
            dataType: 'json',
            success:function(data){
                if(data.error)
                {
                    console.log(data.error);
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
})()