(function(){
    $(function(){
        var origin  = window.origin.toString();
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
        // console.log(origin);
        $('a.public_home_link').attr('href', origin);
    })
})()