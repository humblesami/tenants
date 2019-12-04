(function(){
    console.log('Error from view')
    var dom = undefined;
    try{
        dom = $($('#original_error').text())[0].parentNode;
        var summary = dom.getElementById('summary');
        var explanation = dom.getElementById('explanation');
        var traceback = dom.getElementById('traceback');
        var requestinfo = dom.getElementById('requestinfo');

        var description = $(summary).find('h1:first').text();
        var exception_value = $(summary).find('.exception_value').text();
        var location_th = $(summary).find('th:contains("Exception Location:")');
        var location = location_th.parent().text();

        if(description)
        {
            $('#error_display').append('<h3>Description</h3><div>'+description+'</div>');
        }
        else{
            $('#error_display').append('<h3>Description</h3><div>Unknown Error</div>');
        }
        if(exception_value)
        {
            $('#error_display').append('<h3>Value</h3><div>'+exception_value+'</div>');
        }
        if(location)
        {
            $('#error_display').append('<h3>Location</h3><div>'+location+'</div>');
        }
    }
    catch(er){
        try{
            if($('#explanation').text())
            {
                dom = $('<div>' + $('#explanation').text() +'</div>');
                $('#explanation').html(dom);
            }
            else{
                dom = $('<div>' + $('#original_error').text() +'</div>');
                $('#error_display').html(dom);
            }
        }
        catch(er){

        }
    }

})()