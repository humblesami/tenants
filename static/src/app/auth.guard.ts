import { Injectable } from '@angular/core';
import {SocketService} from './socket.service';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

@Injectable()
export class AuthGuard implements CanActivate {

    constructor(private router: Router, private socketService: SocketService) { }
    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {                
        var cuser = window['current_user'].cookie;
        if(cuser && cuser.token)
        {
            return true;
        }
        else
        {            
            window['functions'].hideLoader('route/'+route.routeConfig.path);
            window['functions'].go_to_login();
            return false;
        }
    }
}