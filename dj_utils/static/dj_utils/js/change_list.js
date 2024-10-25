(function(){
    function set_max_td_width(){
        let table_width = $('#result_list').width();
        let col_count = $('#result_list thead tr th').length;

        let max_td_with = table_width;
        if(col_count > 1){
            if(col_count>5){
                col_count = 5;
            }
            max_td_with = table_width / col_count;
            if(max_td_with < 200)
            {
                max_td_with = 200;
            }
            $('#result_list').prepend(`
            <style>
                #result_list td
                {
                    max-width: ${max_td_with}px
                }
            </style>
            `);
        }
    }
    window.set_max_td_width = set_max_td_width;
    $(function(){
        function set_el_height(el, margin=0) {
            if(!el){
                return;
            }
            let w_top = el.getBoundingClientRect().top;
            w_top = 'calc(100vh - '+(w_top + margin)+'px)';
            $(el).css({'max-height': w_top});
        }
        set_el_height(document.getElementById('nav-sidebar'),10);
        set_el_height(document.getElementById('result_list'), 10);
    });
})();

