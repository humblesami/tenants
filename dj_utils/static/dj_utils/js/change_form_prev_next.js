(function(){
    let loc = window.location.pathname; // ===> /admin/elections/party/7/change/
    let arr = loc.split('/');

    let api_path = '/utils/get-next-prev-id';
    let full_url = window.location.origin + api_path;
    if(arr.length < 5)
    {
        return;
    }
    if(isNaN(arr[4])){
        if(arr[4] != 'add')
        {
            console.log(arr[4], ' should be number');
        }
        return;
    }

    let options = {
        url: full_url,
        beforeSend: function(a, b){

        },
        data: {
            app: arr[2],
            model: arr[3],
            row_id: arr[4]
        },
        success: function(data){
            if(data.prev){
                let record_path = loc.replace('/'+arr[4]+'/', '/'+data.prev+'/')
                $('.prev_next').append('<a href="'+record_path+'">Prev</a>')
            }
            if(data.next){
                let record_path = loc.replace('/'+arr[4]+'/', '/'+data.next+'/')
                $('.prev_next').append('<a href="'+record_path+'">Next</a>')
            }
        },
        error: function(er){

        }
    };
    $.ajax(options);
})();