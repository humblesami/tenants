(function(){
    // const { Observable } = rxjs;
    window['dynamic_files'] = {};
    
    function load_lib(obj_this, on_load){        
        if(!obj_this.status)
        {
            obj_this.status = 'loading';
            
            if(on_load)
            {
                obj_this.call_backs.push(on_load);
            }
            for(var link_path of obj_this.style_paths)
            {
                var link  = document.createElement('link');
                link.rel  = 'stylesheet';
                link.type = 'text/css';
                link.href = link_path;
                link.media = 'all';
                document.head.appendChild(link);
            }
            var len = obj_this.script_paths.length;
            for(var script_path of obj_this.script_paths)
            {
                var script = document.createElement('script');                
                script.onload = function(){
                    obj_this.loaded += 1;
                    if(obj_this.loaded == len)
                    {
                        obj_this.status = 'loaded';
                        for(var cb of obj_this.call_backs)
                        {
                            cb();
                        }
                    }
                };
                script.src = script_path;
                document.body.appendChild(script);
            }
        }
        else{
            if(on_load)
            {
                if(obj_this.status == 'loaded')
                {
                    on_load();
                }
                else{
                    obj_this.call_backs.push(on_load);
                }
            }
        }
    }
    
    var app_libs = window['app_libs'] = {
        test:{
            lib_type: 'test',
            script_paths:[
                "/static/assets/test.js",                
            ],
            style_paths:[            
            ],
            call_backs: [],
            subscriber : function(observer){
                let obj_this = app_libs.pdf;
                if(!obj_this.status)
                {
                    obj_this.call_backs.push(function(data){
                        observer.next(data);
                    });
                    obj_this.status = 'loading';
                    for(var link_path of obj_this.style_paths)
                    {
                        var link  = document.createElement('link');
                        link.rel  = 'stylesheet';
                        link.type = 'text/css';
                        link.href = link_path;
                        link.media = 'all';
                        document.head.appendChild(link);
                    }
                    var len = obj_this.script_paths.length;
                    for(var script_path of obj_this.script_paths)
                    {
                        var script = document.createElement('script');                
                        script.onload = function(){
                            obj_this.loaded += 1;
                            if(obj_this.loaded == len)
                            {
                                obj_this.status = 'loaded';
                                for(let fun of obj_this.call_backs)
                                {
                                    fun('Loaded on first load');
                                }
                                obj_this.call_backs = [];
                            }
                        };
                        script.src = script_path;
                        document.body.appendChild(script);
                    }
                }
                else{
                    if(obj_this.status == 'loaded')
                    {
                        observer.next('Already loaded');
                    }
                    else{
                        obj_this.call_backs.push(function(data){
                            observer.next('Loaded for later subscribler');
                        });
                    }
                }
            },
        },
        moment:{
            script_paths:[
                "static/assets/libs/js/moment.js"
            ],
            style_paths:[],
            load: function(on_load){
                var obj_this = this;    
                load_lib(obj_this, on_load);
            }
        },
        doc_edit:{
            script_paths:[
                "static/assets/fileinput/file.js",
                "static/assets/fileinput/upload_single_file.js"            
            ],
            style_paths:[
                "static/assets/fileinput/css/fileinput.css"
            ],
            load: function(on_load){
                var obj_this = this;
                load_lib(obj_this, on_load);
            }
        },
        jquery_ui: {
            script_paths:[
                "static/assets/libs/js/jquery-ui.min.js",
            ],
            style_paths:[
                "static/assets/libs/css/jquery-ui.css",
                "static/assets/libs/select2/default.theme.css"
            ],
            load: function(on_load){
                var obj_this = this;
                load_lib(obj_this, on_load);
            }
        },
        zebra:{
            style_paths:[
                "static/assets/libs/zebra/zebra_datepicker.css"
            ],
            script_paths:[
                "static/assets/libs/zebra/zebra_datepicker.src.js"
            ],
            load: function(on_load){
                var obj_this = this;    
                load_lib(obj_this, on_load);
            }
        },
        rtc:{
            script_paths:[
                "static/assets/rtc/adapter.js",
                "static/assets/rtc/RTCMultiConnection.min.js",
                "static/assets/rtc/getScreenId.js",
                "static/assets/rtc/getHTMLMediaElement.js",
                "static/assets/rtc/conference.js"
            ],
            style_paths:[],
            load: function(on_load){            
                var obj_this = this;    
                load_lib(obj_this, on_load);            
            }
        },
        pdf:{
            lib_type: 'pdf',
            script_paths:[
                "static/assets/annotator/shared/pdf.js",
                "static/assets/annotator/shared/pdf.viewer.js",
                "static/assets/annotator/annotator.js"
            ],
            style_paths:[
                "static/assets/annotator/shared/pdf.viewer.css",
                "static/assets/annotator/shared/custom.css",
            ],
            load: function(on_load){            
                var obj_this = this;
                app_libs.signature.load(function(){
                    load_lib(obj_this, on_load);
                });
            }
        },
        file_input:{
            script_paths : [
                'https://apis.google.com/js/api.js',
                'https://www.dropbox.com/static/api/2/dropins.js',
                'static/assets/fileinput/js/cloudpicker.js',            
            ],
            style_paths : [],        
            load: function(on_load){            
                var obj_this = this;    
                if(!obj_this.status)
                {
                    obj_this.status = 'loading';
                    var scr_length = obj_this.script_paths.length;
                    for(var scr_path of obj_this.script_paths)
                    {
                        var script = document.createElement('script');
                        if(scr_path == 'https://www.dropbox.com/static/api/2/dropins.js')
                        {
                            script.id = 'dropboxjs';
                            script.setAttribute('data-app-key','pvbda3hm0tpwnod');
                        }
                        script.onload = function(){
                            obj_this.loaded += 1;
                            if(obj_this.loaded == scr_length)
                            {
                                obj_this.status = 'loaded';
                                on_load();
                            }
                        };
                        script.src = scr_path;
                        document.body.appendChild(script);
                    }
                }
                else{
                    if(obj_this.status == 'loaded')
                    {
                        on_load();
                    }
                }
            }
        },
        full_calendar:{
            script_paths : ['static/assets/libs/fullcalendar/fullcalendar.min.js'],
            style_paths : ['static/assets/libs/fullcalendar/fullcalendar.css'],
            status: undefined,
            call_backs: [],
            load: function(on_load){            
                var obj_this = this;    
                load_lib(obj_this, on_load);
            }
        },
        signature: {
            script_paths: [
                'static/assets/libs/signature/signature.js',                
                'static/assets/js/custom_signature.js'
            ],
            style_paths: [],
            load: function(on_load){                
                var obj_this = this;
                app_libs.jquery_ui.load(function(){
                    load_lib(obj_this, on_load);
                });
            }
        },
        bootbox:{
            script_paths : ['static/assets/libs/bootstrap/bootbox.js'],
            style_paths: [],
            load: function(on_load){            
                var obj_this = this;
                load_lib(obj_this, on_load);
            }
        },
        emoji_picker:{
            script_paths : ['static/assets/emoji/js/emoji-picker.js'],
            style_paths:['static/assets/css/emoji.css'],
            load: function(on_load){
                var obj_this = this;    
                load_lib(obj_this, on_load);
            }
        },
        chart: {
            script_paths : ['static/assets/js/chart.js'],
            style_paths : [],
            load: function(on_load){            
                var obj_this = this;    
                load_lib(obj_this, on_load);
            }
        },
        mask: {
            script_paths : ['static/assets/js/mask.js'],
            style_paths : [],
            load: function(on_load){            
                var obj_this = this;
                load_lib(obj_this, on_load);
            }
        },
        duration_picker: {
            script_paths : ['static/assets/libs/duration-picker/duration-picker.js'],
            style_paths : ['static/assets/libs/duration-picker/duration-picker.css'],
            load: function(on_load){            
                var obj_this = this;
                // console.log(43343);
                load_lib(obj_this, on_load);
            }
        }
    };
    
    for(var key in app_libs)
    {
        let obj_this = app_libs[key];
        obj_this.status = undefined;
        obj_this.loaded = 0;
        obj_this.call_backs = [];
        // if(obj_this.subscriber)
        // {
        //     obj_this.load_observable = new Observable(obj_this.subscriber);
        // }
    }
    app_libs.jquery_ui.load();
    app_libs.signature.load();
    app_libs.doc_edit.load();
    app_libs.bootbox.load(function(){
        if(!bootbox)
        {
            console.log('not loaded', app_libs['bootbox']);
        }        
        else{
            window['bootbox'] = bootbox;
        }
    });
    app_libs.moment.load();
})()
