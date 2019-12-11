
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

var network_config = {
	server_base_url:'http://172.16.21.170:8000',
	live : false,
	site_url: '',
    chat_server : 'http://172.16.21.170:'+chat_ser_port,
	show_logs : ['socket','ajax_before','ajax_success']
};

var network_config_https = {
	server_base_url:'https://172.16.21.170:8000',
	live : false,
	site_url: '',
    chat_server : 'https://172.16.21.170:'+chat_ser_port,
	show_logs : ['socket','ajax_before','ajax_success']
};

var site_config = {};
var is_localhost = false;
var current_site_base_url = window.location.protocol+'//' + window.location.hostname + '';
if(current_site_base_url.indexOf('localhost') > -1)
{
    site_config = site_config_local;
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
console.log(site_config);