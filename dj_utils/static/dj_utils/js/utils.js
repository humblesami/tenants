var json_utils = {
    sort_list_by_prop: function(arrayOfObjects, prop_name){
        var byDate = arrayOfObjects.slice(0);
        byDate.sort(function(a,b) {
            return a[prop_name] - b[prop_name];
        });
        return byDate;
    },

    add_delete_url_param: function(){

    }
}
