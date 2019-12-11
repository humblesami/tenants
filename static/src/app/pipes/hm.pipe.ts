import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'hm'})
export class HourMinutesPipe implements PipeTransform {
    transform(seconds: any): string {
        return seconds_to_hour_minutes(seconds);
    }
}

function seconds_to_hour_minutes(seconds) {        
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
}
