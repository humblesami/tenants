import { Component, OnInit } from '@angular/core';
import {SocketService} from "../../app/socket.service";

@Component({
    selector: 'app-messageicon',
    styleUrls:['./messageicon.css'],
    templateUrl: './messageicon.component.html'
})
export class MessageiconComponent implements OnInit {

    socketService: SocketService
    constructor(private ss: SocketService) {
        this.socketService = ss;
    }
    odoo_build = window['odoo'] ? 1 : undefined;
    ngOnInit() {}
}