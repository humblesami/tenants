$(function(){
    var curl = window.location.toString();
    var modules = $('#content-main>.module');
    if(!curl.endsWith('admin') && !curl.endsWith('admin/'))
    {
        modules.show();
        return;
    }
    var hostname = window.location.hostname;        
    var arr = hostname.split('.');
    
    if(arr.length > 1){
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