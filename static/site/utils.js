(function(){
    var js_utils = {
        get_param:function(p_name, url = window.location.toString()){
            const urlParams = new URLSearchParams(window.location.search);
            const myParam = urlParams.get(p_name);
            return myParam
        },
    }
    window['js_utils'] = js_utils;    
    // console.log(window['js_utils']);
})()