import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'formatTime'})
export class FormatTimePipe implements PipeTransform {
    transform(minutes: any, arg: any): string {
        return decimal2time(minutes);
    }
}

function addZeroToUnder10(d)
{
    if(d<10)
        d = "0"+d;
    return d;
}

function decimal2time(decimalTime) {
    var clockTime = '0:00';
    try{
        let hrs = parseInt(decimalTime);
        let min = Math.round((decimalTime - hrs) * 60);
        hrs = addZeroToUnder10( parseFloat( hrs.toString()));
        min = addZeroToUnder10( parseFloat( min.toString()));
        clockTime = hrs + ':' +min;
    }
    catch(er){}
    return clockTime;
}
