(function(){
    
    var me = document.currentScript;
    let me_path = me.src.replace(window.location.origin+'', '');

    const newNode = document.createElement("script");
    newNode.async = false;    
    newNode.src = get_src(me_path);
    let ref_node = document.querySelector('script[src="'+me_path+'"]');
    ref_node.parentNode.insertBefore(newNode, ref_node);
    
    function get_src(me_path){
        let online_path = 'https://momentjs.com/downloads/moment-with-locales.min.js';
        let arr = me_path.split('/');
        let mpath = me_path.replace('/' + arr[arr.length - 1], '/moment.js');
        return mpath;
    }
})();

class DateUtils {
    static add_interval(interval_type, inc, dt) {
        inc = parseFloat(inc);
        if (!dt) {
            dt = moment();
        }
        if (interval_type === 'y') {
            dt = moment(dt).add(inc, 'years');
        }
        if (interval_type === 'mm') {
            dt = moment(dt).add(inc, 'months');
        }
        if (interval_type === 'w') {
            dt = moment(dt).add(inc, 'weeks');
        }
        if (interval_type === 'd') {
            dt = moment(dt).add(inc, 'days');
        }
        if (interval_type === 'h') {
            console.log(inc, dt);
            dt = moment(dt).add(inc, 'hours');
            console.log(inc, dt._i);
        }
        if (interval_type === 'm') {
            dt = moment(dt).add(inc, 'minutes');
        }
        if (interval_type === 's') {
            dt = moment(dt).add(inc, 'seconds');
        }
        console.log(dt);
        return dt._d;
    }

    static test_date(res, pattern = /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/){
        try{
            let tested = Date.parse(res);
            tested = pattern.test(res);
            if (tested){
                return res;
            }
            else{
                //console.log('Is a valid date but invalid foramt => '+res);
            }
            return '';
        }
        catch(er){
            console.log('Not a valid date '+res);
        }
    }

    static add_interval_format(interval_type, format, inc, dt){
        let res = DateUtils.add_interval(interval_type, inc, dt);
        if(format == 'array'){
            res = moment(res).format('YYYY-MM-DD HH:mm:ss');
            res = res.split(' ');
        }
        return res;
    }

    static time_difference(interval_type, start_time, end_time) {
        if (!end_time) {
            end_time = moment();
        }
        start_time = moment.utc(start_time);
        end_time = moment.utc(end_time);
        const diff = moment.duration(end_time.diff(start_time));
        let res = '';
        switch (interval_type) {            
            case 's':
                res = diff.seconds(); break;                
            case 'm':
                res = diff.minutes(); break;
            case 'h':
                res = diff.hours(); break;   
            case 'd':
                res = diff.days(); break;    
            case 'w':
                res = diff.weeks(); break;
            case 'mm':
                res = diff.months(); break;
            case 'y':
                res = diff.years(); break;
            default:
                console.log(interval_type, 444);
                res = '';
                if (diff.years()) {
                    res += `, ${diff.years()} years`;
                }
                if (diff.months()) {
                    res += `, ${diff.months()} months`;
                }
                if (diff.weeks()) {
                    res += `, ${diff.weeks()} weeks`;
                }
                if (diff.days()) {
                    res += `, ${diff.days()} days`;
                }
                if (diff.hours()) {
                    res += `, ${diff.hours()} hours`;
                }
                if (diff.minutes()) {
                    res += `, ${diff.minutes()} minutes`;
                }
                if (diff.seconds()) {
                    res += `, ${diff.seconds()} seconds`;
                }
                if (res.substring(0, 2) === ', ') {
                    res = res.substring(2);
                }
        }
        return res;
    }
}