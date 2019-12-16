$(function(){
    function launchOneDrivePicker(e) {
        var file_type = $('input[name="file_type"]').val();
        let extentions = '';
        if (file_type == 'document')
        {
            extentions = "folder,.pdf,.doc,.docx,.html,.xls,.pptx,.ppt,.txt";
        }
        else
        {
            extentions = ".png,.jpg,.jpeg";
        }
        console.log(file_type);
        var one_keys = {
            'meetvue.com' : "df45ae45-68bd-4568-a473-4159a1b16fc1",
            'boardsheet.com' : "edcfe98f-e101-4041-9510-0a846e0d3a0d",
            'localhost' : "df45ae45-68bd-4568-a473-4159a1b16fc1",
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
            multiSelect: true,
            openInNewWindow: true,
            advanced: {
                filter: extentions
            },
            success: function (response) {
                // console.log(555, response);
                var selection_info = [];
                for(var file of response.value)
                {
                    // console.log(file, 188);
                    selection_info.push({
                        id: file.id,
                        name: file.name,
                        url: file["@microsoft.graph.downloadUrl"],
                        size: file.size,
                        source: 'Onedrive'
                    })
                }
                
                var post_data = {files:selection_info, cloud_number: cloud_number};                
                window.parent.postMessage(post_data, '*');
            },
            cancel: function (response) { console.log(response); },
            error: function (e) { console.log(e); }
        };
        OneDrive.open(odOptions);
    }    
    $("#OpenOne").click(launchOneDrivePicker);
})