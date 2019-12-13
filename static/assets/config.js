
var chat_ser_port = 3000;
var site_config_live = {
	server_base_url:'https://boardsheet.com',
	server_db : 'demo1',
	site_url: 'https://boardsheet.com',
	live : true,
    chat_server : 'https://chat.brainpbx.com',
    app_name : 'BoardSheet',
	show_logs : []
};

var site_config_local = {
	server_base_url:'http://localhost:8000',
	live : false,
	site_url: 'http://localhost',
    chat_server : 'http://localhost:'+chat_ser_port,
	show_logs : ['socket', 'ajax_before'] //, 'ajax_success'
};


var site_config = {};
var is_localhost = false;
var site_port = window.location.port;
if(site_port)
{
    site_port = ':'+site_port
}
var current_site_base_url = window.location.protocol+'//' + window.location.hostname + site_port;

let root_host_name = '';
(function(){
    let h_arr = window.location.hostname.toString().split('.');    
    if(h_arr.length > 1)
    {
        h_arr.splice(0,1);
        root_host_name = h_arr.join('.');
        root_host_name = window.location.protocol + '//' + root_host_name + site_port;        
    }
})()
if(current_site_base_url.indexOf('localhost') > -1)
{
    site_config = site_config_local;
    site_config.server_base_url = site_config.site_url = current_site_base_url;    
    is_localhost = true;
}
else
{    
    site_config = site_config_live;
    site_config.server_base_url = site_config.site_url = current_site_base_url;
	is_localhost = false;
}
window['site_url'] = site_config.site_url;
window['server_url'] = site_config.server_base_url;

site_config.public_urls = ['login']
site_config['app_name'] = 'meetings';
if(is_localhost)
{
    site_config.is_localhost = 1;
    site_config.trace_request = 1;
}
site_config.trace_request = 1;
window['site_config'] = site_config;
var login_url = root_host_name+'/accounts/login';
site_config.block_login_redirect = 1;
// console.log(site_config);