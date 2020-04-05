var js_utils = window['js_utils'] = {
    read_file: function(file, call_back) {
        var reader = new FileReader();        
        reader.readAsDataURL(file, "UTF-8");
        reader.onload = function (evt) {
            // console.log(evt.target.result,1233);
            call_back(evt.target.result);
        }
        reader.onerror = function (evt) {
            console.log(evt, 333);
        }
    }
}