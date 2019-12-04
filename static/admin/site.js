$(function(){
    var curl = window.location.hostname;
    var modules = $('#content-main>.module');    
    var arr = curl.split('.');
    // console.log(arr);
    if(arr.length > 1){
        modules.show();
        $('body').addClass('tenant-app');
        var module_selector = '#content-main .module caption';
        module_selector += ':not(.tenant-app)';        
        $(module_selector).closest('.module').hide();        
    }
    else{        
        $('body').addClass('shared-app');
        modules.hide();
        modules.eq(0).show();
        modules.eq(1).show();
    }
})