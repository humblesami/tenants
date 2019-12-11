import { Component, OnInit, Input } from '@angular/core';
import {SocketService} from '../../app/socket.service';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-breadcrumb',
    templateUrl: './breadcrumb.component.html',
    styleUrls: ['./breadcrumb.component.css']
})
export class BreadcrumbComponent implements OnInit {
    @Input() public create: number;
    @Input() public edit: number;
    @Input() public delete: number;
    @Input() public model:string;
    @Input() public rid:number;
    @Input() public app:string;
    @Input() public title:string;
    @Input() public routes : any;

    route_links: any;
    socketService: any;

    constructor(private sserv : SocketService) { 
        this.socketService = sserv;
        if(this.create){
            this.create_button = true;          
        }
        if(this.edit){
            this.edit_button = true;
        }
        if(this.delete){
            this.delete_button = true;
        }
        this.route_links = [];
    }

    create_button = false;
    edit_button = false;
    delete_button = false;

    ngOnInit() {
        if(this.routes)
        {
            try{
                //console.log(this.app, this.model, this.rid, this.routes);
                this.route_links = JSON.parse(this.routes);
            }
            catch(er){
                console.log(er, this.routes);
            }
        }
    }
}
