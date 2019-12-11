import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'firstToUpper'
})
export class StringFirstToUpperPipe implements PipeTransform {

transform(value: any, args?: any): any {
    if(!value)
    {
        return '';
    }
    var result = value.toLowerCase().split(' ');

    for(var i=0 ; i<result.length; i++){
        result[i] = result[i].charAt(0).toUpperCase() + result[i].substring(1);
    }    
    result =  result.join(' ');
    return result;
}

}
