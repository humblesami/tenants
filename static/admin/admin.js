$(function(){
    var curl = window.location.toString();    
    if(!curl.endsWith('admin') && !curl.endsWith('admin/'))
    {
        return;
    }
    var hostname = window.location.hostname;    
    var modules = $('#content-main>.module');
    var arr = hostname.split('.');
    
    if(arr.length > 1){
        //public tenant        
        // $('body').addClass('tenant-app');
        // let module_selector = '#content-main .module .tenant-app';         
        // $(module_selector).closest('.module').show();
        let tenant_apps = [
            'auth_t',
            'tenant_only',
        ]
        for(let app of tenant_apps)
        {
            $('#content-main .app-'+app+'.module').show();
        }
    }
    else{        
        //customer tenant
        // modules.show();
        // $('body').addClass('shared-app');
        // let module_selector = '#content-main .module .tenant-app';
        // $(module_selector).closest('.module').hide();
        let shared_apps = [
            'customers',
            'auth',
        ]
        for(let app of shared_apps)
        {
            $('#content-main .app-'+app+'.module').show();
        }
    }
})