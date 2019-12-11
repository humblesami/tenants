window['json_functions'] = {
	compare_json_to_sort : function(x, y){
		return x > y ? 1 : x < y ? -1 : 0;
	},
	sort_by_key: function (arr, key) {
		return arr.sort(function(a, b) {
			var x = a[key]; var y = b[key];
			return ((x < y) ? -1 : ((x > y) ? 1 : 0));
		});
	},
	sort_by_2keys : function(arr, key1, key2){
		arr.sort(function(a, b){
			return json_functions.compare_json_to_sort(
				[json_functions.compare_json_to_sort(b[key1], a[key1]), -json_functions.compare_json_to_sort(b[key2], a[key2])],
				[json_functions.compare_json_to_sort(a[key1], b[key1]), -json_functions.compare_json_to_sort(a[key2], b[key2])]
			);
		});
		return arr;
	},
	sort_object: function (chat_users) {

	},
	findWithAttrs: function(array, attr_values) {
		for(var i = 0; i < array.length; i += 1) {
			var all_ok = true;
			for (var attr in attr_values)
			{
				if(array[i][attr] != value) {
					all_ok = false;
					break;
				}
			}
			if(all_ok)
				return i;			
		}
		return -1;
    },
    url_last_segment: function(){
        return this.last_segment(window.location.href,'/');
    },
    last_segment: function(full_str, separator){
        return full_str.substring(full_str.lastIndexOf(separator) + 1)
    },
    get_url_path:function(){
        var curl = window['site_url'];
        curl = window.location.toString().replace(curl, '');
        var i = curl.indexOf('#');
        if(i == 1)
        {
            curl = curl.substr(2);
        }
        return curl;
    },
    find_activate_link: function(selector, path){
        if(!path)
        {
            path = this.get_url_path();
        }
        // console.log(selector, path);
        $(selector).find('a').each(function(i, el){
            if($(el).attr('routerlink') == path)
            {
                $(el).addClass('active');
            }
        });
    }
}