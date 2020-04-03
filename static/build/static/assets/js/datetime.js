
var dt_js = {
    monthNames : [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    monthShortNames : [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ],
    dt_hour_minutes: function(dt) {
        if (typeof(dt) == "string")
            dt = new Date(dt);
        var hour = dt.getHours();
        var minut = dt.getMinutes();
        if (minut < 10) {
            minut = '0' + minut;
        }
        return hour + ':' + minut;
    },
    seconds_to_hour_minutes: function(seconds) {        
        var minutes = Math.floor(seconds / 60);
        var hours = Math.floor(minutes / 60);        
        var minutes = minutes % 60;
        var minutes_str = minutes.toString();
        var hours_str = hours.toString();
        
        if (hours < 10){
            hours_str = "0" + hours;
        }
        if(minutes < 10){
            minutes_str  = "0" + minutes;
        }
        return  hours_str + ":" + minutes_str;
    },
    hours_to_hoursNminutes: function (hours) {
        var res = parseInt(hours);
        var minutes = hours % res;
        minutes = minutes * 60;
        minutes = Math.round(minutes);
        if(res < 10)
            res = "0" + res;
        if (minutes < 10)
            minutes = "0"+minutes;
        res = res +":"+ minutes;
        return res;
    },
    standeredTime: function(dt){
        if(!dt)
        {
            dt = new Date();
        }
    },
    getTimeString: function (dt)
    {
        if (!dt)
            dt = new Date();
        else if (typeof dt == 'string')
            dt = new Date(dt);
    
        var mm = dt.getMinutes();
        var h = dt.getHours();
        var s = dt.getSeconds();
        if (h < 10)
            h = "0" + h;
        if (mm < 10)
            mm = "0" + mm;
        if (s < 10)
            s = "0" + s;
        return h + ":" + mm + ":" + s;
    },
    getMeetingTime: function (dt)
    {
        dt = this.getDateVals(dt)
        var postfix = 'AM';
        if(dt.hours > 12)
        {
            dt.hours = dt.hours%12;
            postfix = 'PM'
        }
        dt.hours = this.addZero(dt.hours);
        dt.minutes = this.addZero(dt.minutes);        
        return dt.hours + ":" + dt.minutes+ ' '+postfix;
    },
    getDateTimeString: function(dt) {
        if (!dt)
            dt = new Date();
        else if (typeof dt == 'string')
            dt = new Date(dt);
        var dat = this.getDateString(dt);
        var tam = this.getTimeString(dt);
        return dat + " " + tam;
    },
    meeting_time: function(dt){
        var obj_this = this;
        if(typeof(dt) == 'string')
        {
            dt = new Date(dt);
        }
        var res = {
            month_year: obj_this.monthShortNames[dt.getMonth()] +' '+dt.getFullYear(),
            day: dt.getDate(),
            time: obj_this.getMeetingTime(dt),
        }
        // console.log(dt, res);
        return res;
    },
    meeting_time_str: function(dt){
        var obj_this = this;
        if(typeof(dt) == 'string')
        {
            dt = new Date(dt);
        }
        var res = obj_this.monthShortNames[dt.getMonth()];
        res += ','+dt.getFullYear();
        res += ' '+dt.getDate();
        res += ' '+obj_this.getMeetingTime(dt);        
        return res;
    },
    getDateVals: function(dt){
        dt = this.get_dt(dt);
        return {
            month: dt.getMonth(),
            year: dt.getFullYear(),
            date: dt.getDate(),
            hours: dt.getHours(),
            minutes: dt.getMinutes(),
            seconds: dt.getSeconds(),
            milli: dt.getMilliseconds(),
        }
    },
    getDateString: function(dt){        
        dt = this.getDateVals(dt);
        dt.year +'-'+ this.addZero(dt.month) +'-'+ this.addZero(dt.date);
    },
    getStandardDate: function(dt){
        dt = this.getDateVals(dt);
        var month = this.monthShortNames[dt.month];
        var res = month + ' '+this.addZero(dt.date)+','+dt.year;
        return res;
    },
    getStandardDateTime: function(dt){
        console.log(dt);
        var res = this.getStandardDate(dt)+' '+this.getMeetingTime(dt);
        return res;
    },
    get_dt: function(dt){
        if (typeof(dt) == 'datetime')
        {
            return dt;
        }
        if(!dt)
        {
            dt = new Date()
        }
        else{
            dt = new Date(dt);            
        }
        return dt;
    },
    date: function(dt){
        this.getDateString(dt);
    },
    now: function(){
        return this.getDateTimeString();
    },
    addZero: function(val){
        if(val < 10)
        {
            val = '0'+val;
        }
        return val;
    },
    addInterval: function(interval_type, n, dt){          
        dt = this.get_dt(dt);
        switch(interval_type){
            case 'y':
                dt.setFullYear(dt.getFullYear() + n);
                break;
            case 'M':
                dt.setMonth(dt.getMonth() + n);
                break;
            case 'd':
                    dt.setDate(dt.getDate() + n);
                break;
            case 'h':
                    dt.setHours(dt.getHours() + n);
                    break;
            case 'm':
                    dt.setMinutes(dt.getMinutes() + n);
                    break;
            case 's':
                    dt.setSeconds(dt.getSeconds() + n);
                break;
            case 'ms':
                    dt.setMilliseconds(dt.getMilliseconds() + n);
                break;        
        }
        return dt;
        // console.log(dt), 133;
    },
    now_full: function(){
        var res = dt_js.getTimeString()+ '.'+ new Date().getMilliseconds();
        return res;
    },
    timeAgo: function(value){
        if (value) {
            var seconds = Math.floor((+new Date() - +new Date(value)) / 1000);
            if (seconds < 29 && seconds > -1)
                return 'Just now';

            const intervals = {
                'year': 31536000,
                'month': 2592000,
                'week': 604800,
                'day': 86400,
                'hour': 3600,
                'minute': 60,
                'second': 1
            };
            let counter;
            var is_minus = false;
            if(seconds < 0)
            {
                is_minus =true;
                seconds *= -1;
            }
            for (const i in intervals) {
                counter = Math.floor(seconds / intervals[i]);
                if (counter > 0)
                {
                    if (counter === 1) {
                        if(is_minus)
                        {
                            return 'in '+counter +' '+i;
                        }
                        else
                        return counter + ' ' + i + ' ago'; // singular (1 day ago)
                    } else {
                        if(is_minus)
                        {
                            return 'in '+counter +' '+i+'s';
                        }
                        else
                        return counter + ' ' + i + 's ago'; // plural (2 days ago)
                    }
                }
            }
        }
        return value;
    }
}
window['dt_functions'] = dt_js;