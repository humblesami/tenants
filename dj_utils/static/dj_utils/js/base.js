$(function(){
    let host_name = window.location.hostname;
    if(host_name.indexOf('adminurdu')>-1){
        $('title').html('Urdu: ' + $('title').html());
    }
    else{
        $('title').html('Eng: ' + $('title').html());
    }
});
var web_utils = {
    search_param: function(param_name, now_url = window.location + ''){
        let params = (new URL(now_url)).searchParams;
        let param_val = params.get(param_name);
        return param_val;
    },
    add_param_to_url: function(now_url, param_name, new_val){
        if(!param_name)
        {
            return now_url;
        }
        let searchParams = new URL(now_url).searchParams;
        let remade = [];

        let found = false;
        searchParams.forEach(function(val, nam){
            if(nam == param_name){
                found = true;
                remade.push(param_name+'='+new_val);
            }
            else{
                remade.push(nam+'='+val);
            }
        });

        if(!found){
            remade.push(param_name+'='+new_val);
        }
        qs_now = remade.join('&');
        let updated_url = window.location.origin + window.location.pathname+'?'+qs_now;
        return updated_url;
    }
}