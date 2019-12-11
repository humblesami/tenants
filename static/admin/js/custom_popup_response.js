/*global opener */
(function() {
    var path = window.location.pathname.split('/');
    var initData = JSON.parse(document.getElementById('django-admin-popup-response-constants').dataset.popupResponse);
    var length = path.length
    var model = '';
    var action = '';
    var id = undefined;
    if (length == 4)
    {
        model = path[1]
        id = path[2]
        action = 'survey_submit'
    }
    else
    {
        model = path[3]
        action = path[length-2];
        id = path[4]
    }
    
    var data = {"model":model,"action":action,"id":id, "obj": initData.obj}
    window.parent.postMessage(data, '*');
})();
