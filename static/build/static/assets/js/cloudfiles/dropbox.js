$(function(){
    
    var access_token = undefined;
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

    function open_files() {
        access_token = localStorage.getItem("dropbox/token");
        if(!access_token)
        {
            init_token();
            return;
        }
     //   var token = localStorage.getItem('/dropbox/token');    
        var token = access_token;
     // console.log(token, 24);
        var options = {
            success: function (files) {
                for (const file of files) {
                        const name = file.name;
                        const url = file.link;
                        const file_size = file.bytes;
                        console.log(file);
                    }
            },
            cancel: function () {
            },
            linkType: "direct", // or "preview"
            multiselect: true,
            folderselect: false, // or true
            extensions: ['.pdf', '.doc', '.docx', '.html', '.odt','.xls','.pptx','.ppt'],
        //    sizeLimit: 4096, // or any positive number
        };
        Dropbox.choose(options);
    }
    $("#OpenDropboxFilePicker").click(open_files);
})