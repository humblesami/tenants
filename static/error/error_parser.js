(function(){
    console.log('Error from view')
    var error_text = '';
    var dom = undefined;
    try{
        var error_text = $('#original_error').text();        
        var error_obj = $(error_text);        
        var title = '<h3>' + error_obj[3].innerHTML + '</h3>';
        var error_html = title;
        error_obj.each(function(i, el){
            // console.log(i, el);
            if(i > 10 && i <12 && i % 2 != 0){
                if($(el).is('#summary')){
                    $(el).find('table.meta tbody').children().each(function(j, tr){
                        if(j>5)
                        {
                            $(tr).remove();
                        }
                    })
                }
                error_html += el.outerHTML;
            }
        });
        $('#error_display').html(error_html);
    }
    catch(er){
        $('#error_display').html(error_text);
        // console.log(er);
    }

})()