var js_utils = {
    json: {
        sort_list_by_prop: function(arrayOfObjects, prop_name){
            var byDate = arrayOfObjects.slice(0);
            byDate.sort(function(a,b) {
                return a[prop_name] - b[prop_name];
            });
            return byDate;
        }
    },
    web: {
        add_delete_url_param: function(){

        },
        create_script_element: function(src, onload){
            let js_script = document.createElement('script');
            js_script.src = src;
            js_script.onload = onload;
            return js_script;
        },
        insert_element: function(dom_el){
            document.body.appendChild(dom_el);
        }
    },
    js: {
        get_relative_src: function(cur_src, relative_path, skip=0){
            let arr = cur_src.split('/');
            let arr1 = arr.slice(0, arr.length - 1 - skip);
            res = arr1.join('/') + '/' + relative_path;
            return res;
        }
    },
    django : {
        on_ready: function(){
            let st_prev = localStorage.getItem('#nav-sidebar/scroll/top');
            let side_nav_bar = $('#nav-sidebar');
            if(st_prev) {
                side_nav_bar.scrollTop(st_prev);
            }
            $('#nav-sidebar').scroll(e=>{
                st_now = side_nav_bar.scrollTop();
                localStorage.setItem('#nav-sidebar/scroll/top', st_now);
            });
            //console.log('Will remember the left bar scroll on page load');
        }
    }
}

$(function(){
    if($('#container .main #nav-sidebar.sticky').length)
    {
        js_utils.django.on_ready();
    }
    else{
        console.log('No #container .main #nav-sidebar.sticky found');
    }
});
