var js_utils = window['js_utils'] = {    
    move_element: function(arr, old_index, new_index){
        while (old_index < 0) {
            old_index += arr.length;
        }
        while (new_index < 0) {
            new_index += arr.length;
        }
        if (new_index >= arr.length) {
            var k = new_index - arr.length + 1;
            while (k--) {
                arr.push(undefined);
            }
        }
        arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
        return arr; // for testing purposes
    },
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
    },
    remove_items_by_indices: function(array, indices){
        for(var ind of indices)
        {
            for(var i = 0; i < array.length; i++)
            {
                if(ind == i)
                {
                    array.splice(i, 1);
                    i--;
                }
            }
        }
    },
    unique_id: function(){
        let rand = (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        var now = new Date();
        rand = 'id_'+now.getFullYear()+now.getMonth()+now.getDate()+now.getHours()+now.setSeconds()+rand;
        return rand;
    },
    addLoader: function(element, position){       
        if(element.length != 1)
        {
            if(element.length > 1)
            {
                element = element.last();                
                console.log(element.attr('class') + ' found more than one');
            }
            else{
                console.log(element.attr('class') + ' not found');
                return;
            }
        }
        var pos_type = element.css('position');        
        if(!pos_type || pos_type == 'static')
        {
            element.css('position','relative');
        }
        var partial_loader = $('.partial-loader:first').clone().css('display','flex');
        if(position){
            partial_loader.find('.row').css('justify-content', position);
        }
        element.append(partial_loader);
    },
    removeLoader: function(element){
        if(element.length != 1)
        {
            if(element.length > 1)
            {
                console.log(element);                
                console.log('found more than one');
            }
            else{
                console.log('not found');
                return;
            }
        }
        var loader = element.find('.partial-loader');
        if(loader.length)
        {
            // console.log('removed loader ', element[0]);
            element.find('.partial-loader').remove();
        }
        else
        {
            console.log('loader not found', element[0]);
        }
    },
    camel_case: function(value){
        var result = value.toLowerCase().split(' ');
        for(var i=0 ; i<result.length; i++){
            result[i] = result[i].charAt(0).toUpperCase() + result[i].substring(1);
        }
        result =  result.join(' ');
        return result;
    },
    sort_by_two_keys:function(json_array){
        var cmp = function(x, y){
            return x > y ? 1 : x < y ? -1 : 0; 
        };
        return json_array.sort(function(a, b){
            return cmp( 
                [cmp(a.online, b.online), cmp(a.name, b.name)], 
                [cmp(b.online, a.online), cmp(b.name, a.name)]
            );
        });
    },
    findPos: function(obj, scroll_el) {
        var obj_this = this;
        var childPos = obj.offset();
        var parentPos = scroll_el.offset();
        var childOffset = {
            top:0,
            left:0
        }
        try
        {
            childOffset = {
                top: scroll_el.scrollTop() + childPos.top - parentPos.top,
                left: scroll_el.scrollLeft() + childPos.left - parentPos.left
            }
        }
        catch(er){
            console.log(er);
        }
        return childOffset;
    },
    scroll_to_element: function(focus_el, scroll_el){
        var obj_this = this;
        if(!(focus_el && focus_el.length && focus_el.length ==1)){
            console.log('Invalid focus element ', focus_el);
            if(focus_el.length)
            {
                console.log('With length ', focus_el.length);
            }
        }
        if(!(scroll_el && scroll_el.length && scroll_el.length ==1)){
            console.log('Invalid scroll element ', scroll_el);
            if(scroll_el.length)
            {
                console.log('With length ', scroll_el.length);
            }
        }
        var static_focus_pos = obj_this.findPos(focus_el, scroll_el);
        var position = {
            left: static_focus_pos.left,
            top: static_focus_pos.top,
        }

        // console.log(static_focus_pos,  position);
        
        var focus_el_rect = { 
            width: focus_el.width(),
            height: focus_el.height()
        }
        var scroll_el_rect = { 
            width: scroll_el.width(),
            height: scroll_el.height()
        }

        // console.log(position, 445);
        position.left = position.left -  scroll_el_rect.width /2 + focus_el_rect.width /2;
        if(position.left<0)
        {
            position.left = 0;
        }
        position.top = position.top - scroll_el_rect.height/2 + focus_el_rect.height /2;
        if(position.top<0)
        {
            position.top = 0;
        }

        // var scroll_now_y = scroll_el.scrollTop();
        // var scroll_now_x = scroll_el.scrollLeft();
        var dy = position.top;// - scroll_now_y;
        var dx = position.left;// - scroll_now_x;

        // console.log(position, dy, dx);

        scroll_el.scrollLeft(dx);
        // var distance = Math.abs(position.top - scroll_now_y);
        var animate_time = 500;
        // console.log(distance, 133, animate_time);
        scroll_el.animate({
            scrollTop: dy
        }, animate_time);
    }
}