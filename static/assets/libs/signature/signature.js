var last_drawn_path = [];
jQuery(document).ready(function(e) {
    jQuery.fn.sign = function(options) {
        var params = jQuery.fn.extend({
            reset: options.resetButton ? options.resetButton : null,            
            color: options.color ? options.color : '#000000',
            lineWidth: options.lineWidth ? options.lineWidth : 10,
        }, options);        

        var canvas = jQuery(this);
        // console.log(this[0]);
        var context = canvas.get(0).getContext('2d');
        context.lineWidth = params.lineWidth;
        context.strokeStyle = params.color;
        context.lineCap = 'round';

        var points = [];
        var holdClick = false;

        var touch = function(e)
        {
            var touch = null;
            if (e.type == 'touchstart' || e.type == 'touchend' || e.type == 'touchmove') {
                touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
            } else {
                touch = e;
            }
            return ({x: touch.pageX, y: touch.clientY});
        }

        var getMousePosition = function(canvas, evt)
        {
            var rect = canvas.get(0).getBoundingClientRect();
            var pos = touch(evt);
            var res_pos = {
                x: pos.x - rect.left,
                y: pos.y - rect.top
            };
            return res_pos;
        }

        var draw = function(ctx, x, y)
        {
            points.push({x: x, y: y, break: false});
            var p1 = points[0];
            var p2 = points[1];
            ctx.moveTo(p1.x, p1.y);            
            for (var i = 1; i < points.length; i++) {
                var midPoint = calculateMiddlePoint(p1, p2);
                if (p1.break) {
                    ctx.moveTo(p2.x, p2.y);
                } else {
                    ctx.quadraticCurveTo(p1.x, p1.y, midPoint.x, midPoint.y);
                }
                p1 = points[i];
                p2 = points[i+1];
            }            
            ctx.lineTo(p1.x, p1.y);
            last_drawn_path.push('L ' + p1.x + ' ' + p1.y);
            ctx.stroke();
        }

        var calculateMiddlePoint = function(pointStart, pointEnd)
        {
            return {
                x: pointStart.x + (pointEnd.x - pointStart.x) / 2 ,
                y: pointStart.y + (pointEnd.y - pointStart.y) / 2
            }
        }
        // Mouse & touch events
        var mousePosition_down = {};
        var mouse_doen_time;
        canvas.on('touchstart mousedown', function(e) {
            holdClick = true;
            points = [];
            context = this.getContext('2d');
            last_drawn_path = [];
            context.beginPath();
            var mousePosition = getMousePosition(canvas, e);
            mousePosition_down = mousePosition;
            last_drawn_path.push('M ' + mousePosition.x + ' ' + mousePosition.y);
            points.push({x: mousePosition.x , y: mousePosition.y, break: false});
            mouse_doen_time = new Date();
            return false;
        }).on('touchmove mousemove', function(e)
        {
            if (holdClick) {
                var mousePosition = getMousePosition(canvas, e);                    
                draw(context, mousePosition.x, mousePosition.y);
            }
            return false;
        }).on('touchend mouseup', function(e) {
            e.preventDefault();            
            holdClick = false;
            if(!points.length)
            {
                return;
            }                        
            var mousePosition = getMousePosition(canvas, e);
            // console.log(mousePosition_down, mousePosition, new Date() - mouse_doen_time);
            if(mousePosition_down.x == mousePosition.x && mousePosition_down.y == mousePosition.y){
                if(new Date() - mouse_doen_time < 350)
                {
                    // console.log('No drawinfg');
                    return;
                }
            }
            if(last_drawn_path.length && !last_drawn_path[last_drawn_path.length - 1].startsWith('L '))
            {
                last_drawn_path.push('L ' + mousePosition.x + ' ' + mousePosition.y);
            }
            // console.log(canvas[0].width, canvas[0].height);
            points[points.length - 1].break = true;
            // context.closePath();
            if(context.on_mouse_up)
            {
                context.on_mouse_up();
                reset();
            }
            // console.log($(this).closest('.page').attr('id'));
            return false;
        });

        // Reset canvas
        var reset = function()
        {
            context.clearRect(0, 0, canvas.width(), canvas.height());
            points.length = 0;
        }

        if (params.reset !== null) {
            params.reset.on('click touchend', function()
            {
                reset();
            });
        }
        return context;
    };
});