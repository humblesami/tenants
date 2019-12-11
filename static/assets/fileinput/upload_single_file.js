function upload_single_file(files, resInfo, cloud=false, success)
{
    let obj_this = this;
    // console.log(files, 13);
    for(var obj of files){
        if(!obj.file_name)
        {
            obj.file_name = obj.name;
        }
    }

    $('.file-drop-zone-title').addClass('loading').html('Uploading '+files.length+' files...');
    var url = '';
    if (resInfo.file_type == 'document')
    {
        url = window['site_config'].server_base_url+'/docs/upload-single-file';
    }
    else
    {
        url = window['site_config'].server_base_url+'/docs/upload-single-image-file';
    }
    var formData = new FormData();
    if(!cloud)
    {
        var i= 0;
        for(var file of files){
            formData.append('file['+i+']', file);
            i++;
        }
    }
    else
    {
        formData.append('cloud_data', JSON.stringify(files));
    }
    
    formData.append('res_app', resInfo.res_app);
    formData.append('res_model', resInfo.res_model);
    formData.append('res_id', resInfo.res_id);
    formData.append('res_field', resInfo.res_field);
    formData.append('file_type', resInfo.file_type);
    let user = localStorage.getItem('user');
    user = JSON.parse(user);
    let headers = {'Authorization': 'Token '+user.token};
    var file_input_picker = $('.file-input-picker-container')
    // js_utils.addLoader(file_input_picker);
    // console.log(formData);
    $.ajax({
        url: url,
        data: formData,
        type: 'POST',            
        dataType: 'JSON',
        headers: headers,
        contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
        processData: false, // NEEDED, DON'T OMIT THIS
        success: function(data){
            try{
                var error_message = data.error;
                if(error_message)
                {
                    console.log(error_message);
                    if(error_message.message)
                    {
                        error_message = error_message.message;
                    }
                    $(".feedback-message").append(error_message);
                }
                else
                // console.log($('.file-input-picker-container:visible').closest('.modal:visible').length, 232);
                {
                    success(data);
                    $('.file-input-picker-container:visible').closest('.modal:visible').find('#close-btn').click();
                }
            }
            catch(er){
                console.log(data);
                $(".feedback-message").append('<p id="success-message" class="alert-danger">Invalid data from file save</p>');
                return;
            }
            
        },
        error: function(a,b,c,d){
            $('.feedback-message').append('<p id="success-message" class="alert-danger">Fail to Upload Files </p>').fadeIn("slow");
        },
        complete:function(){
            // js_utils.removeLoader(file_input_picker);
            $('.file-drop-zone-title').removeClass('loading').html('Drag & drop files here …');                
            setTimeout(function(){
                $(".feedback-message").fadeOut("slow");
                $(".feedback-message").html('');
            }, 4000);
        }
    });
}
window['upload_single_file'] = upload_single_file;