$(function(){
    var multiSelect = false;
    var active_picker = undefined;
    var active_cloud_picker = undefined;
    var file_type = '';
    function is_multi_select_enabled(e){
        active_picker = $(e.target).closest('.picker');
        active_cloud_picker = active_picker.closest('.cloud_pickers_container');
        multiSelect = active_cloud_picker.attr('multiple');
        file_type = active_cloud_picker.attr('input_type');
        if(multiSelect)
        {
            multiSelect = true;
        }
        else
        {
            multiSelect = false;
        }
    }

    function init_drop_box_picker(){
        var access_token = undefined;
        function open_cloud_picker(ev) {            
            is_multi_select_enabled(ev);
            access_token = localStorage.getItem("dropbox/token");
            if(!access_token)
            {
                // init_token();
                // return;
            }
            let extensions = [];
            if (file_type == 'document')
            {
                extensions = ['.pdf', '.doc', '.docx', '.html', '.odt','.xls','.pptx','.ppt'];
            }
            else
            {
                extensions = ['.png', '.jpg', '.jpeg'];
            }
            var options = {
                success: function (files) {
                    var selection_info = [];
                    for (const file of files) {
                        // console.log(file, 188);
                        selection_info.push({
                            id: file.id,
                            name: file.name,
                            url: file.link,
                            size: file.bytes,
                            source:'Dropbox',
                        })
                    }
                    on_files_selected(selection_info, 'dropbox');
                },
                cancel: function () {
                },
                linkType: "direct", // or "preview"
                multiselect: multiSelect,
                folderselect: false, // or true
                extensions: extensions,
            //    sizeLimit: 4096, // or any positive number
            };
            Dropbox.choose(options);
        }
        function init_token(){
            if(access_token)
            {
                open_files();
                return;
            }
            var height = window.innerHeight;
            var width = window.innerWidth;
            window.open("/temp/dropbox-authorize", "Dropbox", "width="+width+",height="+height);
        
            var eventMethod = window.addEventListener ? "addEventListener" : "attachEvent";
            var eventer = window[eventMethod];
            var messageEvent = eventMethod == "attachEvent" ? "onmessage" : "message";
            // Listen to message from child window
            eventer(messageEvent,function(e) {
                if(e.data.secret == 'sadasecret')
                {
                    console.log('parent received message!: ', e.data);
                    access_token = e.data.token;
                    open_files();
                }
                else
                {
                    // console.log('Pata ni kon kari janda');
                }
            }, false);
        }
        $('body').on('click', '.drop_box_picker', open_cloud_picker);
    }


    function init_google_picker(){
        var access_token = undefined;
        function open_cloud_picker(ev){
            is_multi_select_enabled(ev);
            if(gapi)
            {
                gapi.load('auth', { 'callback': onAuthApiLoad });
                gapi.load('picker');
            }
            else
            {
                console.log('Google api not loaded yet');
            }
        }
        // 'client_id': '817538782176-9cenjdob9ab7bc60b0eqkvlotpmrkfcg.apps.googleusercontent.com',
        // 'client_id': '921039722572-u3aq7gvjgk42gj590ve3qf5fc1schjf0.apps.googleusercontent.com',
        function onAuthApiLoad() {
            console.log('APi Loaded');
            window.gapi.auth.authorize({
                'client_id': '921039722572-u3aq7gvjgk42gj590ve3qf5fc1schjf0.apps.googleusercontent.com',
                'scope': [
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive.metadata'
                ]
            }, handleAuthResult);
        }
    
        function handleAuthResult(authResult) {
            if (access_token || (authResult && !authResult.error)) {
                access_token = authResult.access_token;
//                console.log(access_token);
                createPicker();
            }
            else
            {
                console.log(authResult);
            }
        }

        function createPicker() {
            var appId = 'boreal-quarter-250721';
            var allowed_types = [];
            if (file_type == 'document')
            {
                allowed_types = [
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/x-vnd.oasis.opendocument.spreadsheet",
                    
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "application/vnd.oasis.opendocument.presentation",
        
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/vnd.oasis.opendocument.text",
                    "application/rtf",
                    "application/pdf"
                ];
            }
            else
            {
                allowed_types = [
                    "image/png",
                    "image/jpg",
                    "image/jpeg",
                ];
            }
            // console.log(allowed_types);
            allowed_types = allowed_types.join(',');
            var view = new google.picker.View(google.picker.ViewId.DOCS);
            view.setMimeTypes(allowed_types);
            var picker_builder = new google.picker.PickerBuilder()
                .setAppId(appId)
                .setOAuthToken(access_token)
                .addView(view)
                .setCallback(pickerCallback);
            if(multiSelect)
            {
                picker_builder.enableFeature(google.picker.Feature.MULTISELECT_ENABLED);
            }
            var gdrive_picker = picker_builder.build();
            gdrive_picker.setVisible(true);        
        }
    
        function pickerCallback(data) {
            if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                var files = data[google.picker.Response.DOCUMENTS];
                if(!files.length)
                {
                    return;
                }
                var selection_info = [];
                for(const file of files)
                {
                    // console.log(file, 188);
                    console.log(access_token);
                    selection_info.push({
                        id: file.id,
                        name: file.name,
                        access_token: access_token,
                        view_url: file.url,
                        url: 'https://www.googleapis.com/drive/v3/files/'+file.id+'?alt=media',
                        size: file.sizeBytes,
                        source:'Google',
                    });
                    // console.log(selection_info[0]);
                }
                on_files_selected(selection_info, 'google');
            }
        }
        $('body').on('click', '.google_drive_picker', open_cloud_picker);
    }

    function init_one_drive_picker(){
        function open_cloud_picker(ev){
            is_multi_select_enabled(ev);
            var one_keys = {
                'meetvue.com' : "df45ae45-68bd-4568-a473-4159a1b16fc1",
                'boardsheet.com' : "edcfe98f-e101-4041-9510-0a846e0d3a0d",
                'localhost:8000' : "df45ae45-68bd-4568-a473-4159a1b16fc1",
            }
            var api_key = '';
            for(var key in one_keys)
            {
                if(window['site_url'].indexOf(key) > - 1) 
                {
                    api_key =  one_keys[key];
                    break;
                }
            }
            if(!api_key){return}
            var odOptions = {
                // df45ae45-68bd-4568-a473-4159a1b16fc1
                clientId: api_key,
                action: "download",
                multiSelect: multiSelect,
                openInNewWindow: true,
                advanced: {
                    // filter: "folder,.pdf,.doc,.docx,.html,.xls,.pptx,.ppt,.txt"
                },
                success: function (files) {
                    var selection_info = [];
                    for(var file of files)
                    {
                        // console.log(file, 188);
                        selection_info.push({
                            id: file.id,
                            name: file.name,
                            url: file["@microsoft.graph.downloadUrl"],
                        })
                    }
                    on_files_selected(files, 'onedrive');
                },
                cancel: function (response) { console.log(response); },
                error: function (e) { console.log(e); }
            };
            OneDrive.open(odOptions);
        }
        $('body').on('click', '.one_drive_picker', open_cloud_picker);
    }

    function on_files_selected(current_files, source){        
        var current_cloud_number = $(".cloud_pickers_container").index(active_cloud_picker);
        // console.log(current_files, current_cloud_number, 3233);
        window['merge_cloud_files'][current_cloud_number](current_files);
    }
    
    init_google_picker();
    init_drop_box_picker();
    // init_one_drive_picker();
})
