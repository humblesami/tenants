import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'keys'})
export class CamelCasePipe implements PipeTransform {
    transform(value, args:string[]) : any {
        let keys = [];
        for (let key in value) {
            keys.push(key);
        }
        return keys;
    }
}
// import { Pipe, PipeTransform } from '@angular/core';

// @Pipe({name: 'camel'})
// export class CamelCasePipe implements PipeTransform {
//   transform(value: string, arg: any) : any {
//     let arr = value.split(' ');
//     let res = arr[0];
//     res = res.substr(0, 1).toUpperCase() + res.substr(1, res.length - 1);    
//     for(let i= 1; i<arr.length; i++)
//     {
//         let temp = arr[1];
//         temp = temp.substr(0, 1).toUpperCase() + temp.substr(1, temp.length - 1);
//         res += ' '+temp;
//     }
//     return res;
//   }
// }