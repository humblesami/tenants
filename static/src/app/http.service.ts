import { Injectable, Output, EventEmitter } from '@angular/core';

declare var $: any

@Injectable()
export class HttpService {
    server_url;
    states = undefined;
    offset: number;
    limit: number;
    count: number;
    total: number;
    search_kw = '';
    @Output() on_paged_data: EventEmitter<any> = new EventEmitter();

    constructor() {
        this.server_url = window['server_url'];
        this.offset = 0;
        this.limit = 5;
        this.count = 0;
    }

    search(input_data: any, success_cb, failure_cb)
    {
        var options = this.makeOptions_search('get', input_data, success_cb, failure_cb);
        window['dn_rpc_object'](options);
    }

    get(input_data: any, success_cb, failure_cb) {
        var options = this.makeOptions_secure('get', input_data,success_cb, failure_cb);
        window['dn_rpc_object'](options);
    }
    post(input_data: any, success_cb, failure_cb) {
        var options = this.makeOptions_secure('post', input_data,success_cb, failure_cb);
        window['dn_rpc_object'](options);
    }
    post_files(form: any) {
        var url = form.attr("action");
        url = window['site_config'].server_base_url + url;
        var formData = {};
        $(form).find("input[name]").each(function (index, node) {
            formData[node.name] = node.value;
        });
        $.post(url, formData).done(function (data) {
            alert(data);
        }).failure(function(a,b,c,d){
            console.log(a,b,c,d);
        });
    }
    post_public(input_data: any, success_cb, failure_cb) {
        var options = this.makeOptions_public(input_data,success_cb, failure_cb);
        window['dn_rpc_object'](options);
    }

    authenticate(url: string, input_data: any, success_cb, failure_cb, complete_cb) {
        const httpservie = this;
        input_data = {
            args:{
                app: 'authsignup',
                model: 'AuthUser',
                method: 'login_user',
            },
            params: input_data
        }
        var options = httpservie.makeOptions_public(input_data, success_cb, failure_cb);
        options.onSuccess = function(data){            
            if(success_cb)
            {
                success_cb(data);
            }
            window['current_user'].onLogin(data);
        };
        options.type = 'get';
        options.onComplete = complete_cb;
        options.onError = failure_cb;
        window['dn_rpc_object'](options);
    }

    make_pages_when_loaded = false;
    makeOptions_secure(type, input_data, success_cb, failure_cb)
    {
        let obj_this = this;
        var onRequestFailed = function(res)
        {
            if(failure_cb)
                failure_cb(res);
        };
        // delete input_data.params.offset;
        // delete input_data.params.limit;
        if(obj_this.search_kw)
        {
            input_data.params.kw = obj_this.search_kw;
        }
        if(!input_data.params)
        {
            input_data.params.limit = obj_this.limit;
            input_data.params.offset = obj_this.offset;
        }
        else{
            if(!input_data.params.limit)
            {
                input_data.params.limit = obj_this.limit;
            }
            if(!input_data.params.offset && input_data.params.offset != 0 )
            {
                input_data.params.offset = obj_this.offset;
            }
        }
        var options = {
            url: '/rest/secure',
            type: type,
            before:function(a, b){
                //console.log(b.url);
            },
            data:input_data,
            //type:'post',
            onSuccess:function(data){
                if(success_cb)
                {
                    success_cb(data);
                }
                if(data.total)
                {
                    obj_this.total = Number(data.total);
                    obj_this.count = Number(data.count);
                    try{
                        obj_this.on_paged_data.emit();
                    }
                    catch{

                    }
                    obj_this.make_pages_when_loaded = true;
                }
                else if(data.total == 0)
                {
                    obj_this.total = 0;
                    obj_this.offset = 0;
                    obj_this.count = 0;
                }
            },
            onError:onRequestFailed,
            onComplete:function(){
            }
        };
        return options;
    }

    makeOptions_search(type, input_data, success_cb, failure_cb)
    {
        var onRequestFailed = function(res)
        {
            if(failure_cb)
                failure_cb(res);
        };
        var options = {
            url: '/rest/search',
            type: type,
            before:function(a, b){
                //console.log(b.url);
            },
            data:input_data,
            //type:'post',
            onSuccess:function(data){
                if(success_cb)
                {
                    success_cb(data);
                }
            },
            onError:onRequestFailed,
            onComplete:function(){
            }
        };
        return options;
    }

    makeOptions_public(input_data, success_cb, failure_cb) {
        const http_service = this;
        var onRequestFailed = function(res)
        {
            if(failure_cb)
                failure_cb(res);
        };
        var options = {
            url: '/rest/public',
            type: 'get',
            before:function(a, b){
                //console.log(b.url);
            },
            data:input_data,
            //type:'post',
            onSuccess: function(data){
                if(success_cb)
                {
                    success_cb(data);
                }
            },
            onError:onRequestFailed,
            onComplete:function(){
            }
        };
        return options;
    }

    make_bread_crumb() {
        let comeplete_url = window.location + '';
        let base_url = window['site_url'] + '';
        let page_url = comeplete_url.replace(base_url + '/', '');

        let ar = page_url.split('/');
        let last_link = '';
        let links = []
        for ( var i in ar) {
            if (parseInt(i) !== ar.length - 1) {
                last_link = last_link + '/' + ar[i];
                links.push({url: last_link, title: ar[i]});
            }
        }
        return links;
    }
}
