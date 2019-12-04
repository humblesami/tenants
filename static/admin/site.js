$(function(){
    var curl = window.location.hostname;
    var module_selector = '#content-main .module caption';
    var arr = curl.split('.');
    // console.log(arr, 4343);
    if(arr.length > 1){        
        $('body').addClass('tenant-app');
        module_selector += ':not(.tenant-app)';
        // console.log(module_selector, $(module_selector)[0]);
        $(module_selector).closest('.module').hide();
    }
    else{
        $('body').addClass('shared-app');
    }
})