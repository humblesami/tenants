import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { range } from 'rxjs';
declare var $: any;
@Component({
    selector: 'app-paginator',
    styleUrls:['./paginator.css'],
    templateUrl: './paginator.component.html'
})
export class PaginatorComponent implements OnInit {
    @Output() reload_data: EventEmitter<any> = new EventEmitter();
    limit_options = [
        2,
        5,
        10,
        50,
        100
    ]
    httpService : any;
    page_number: number;
    shown_pages = [];
    startPage: number;
    endPage: number;
    total_pages = [];

    constructor(private httpServ : HttpService) {        
        // console.log(Date(), new Date().getMilliseconds(), 113);
        this.httpService = httpServ;
        this.httpService.offset = 0;        
        this.page_number = 1;
        // this.httpService.on_paged_data = this.all_pages;
    }

    all_pages(){
        let obj_this = this;
        obj_this.total_pages = [];
        let lPage= Math.ceil(obj_this.httpServ.total/obj_this.httpService.limit);
        for (let i = 1; i <= lPage; i++) {            
            obj_this.total_pages.push(i)
        }
        obj_this.get_pager(obj_this.page_number);
    }

    get_pager(current_page){
        // console.log(current_page, 134);
        if(current_page <= 1){
            this.page_number = 1;
        }
        if(this.total_pages.length <= 5)
        {   
            this.startPage = 1;
            this.endPage = this.total_pages.length;
        }
        else
        {
            if(current_page > 2)
            {
                if(current_page - 2 > 0 && current_page + 2 < this.total_pages.length)
                {
                    this.startPage = current_page - 2;
                    this.endPage = current_page + 2;    
                }
                else
                {
                    this.startPage = this.total_pages.length - 4;
                    this.endPage = this.total_pages.length;
                }
            }
            else{
                this.startPage = 1;
                this.endPage = 5;
            }
        }

        this.shown_pages = this.total_pages.slice(this.startPage - 1, this.endPage);
        // console.log(this.shown_pages);
    }

    page_Data(event) {
        this.httpService.offset = (event - 1) * this.httpService.limit;
        if(event == this.page_number)
        {
            return;
        }
        this.page_number = event;
        this.get_pager(this.page_number);
        this.reload_data.emit();
    }

    change_page(change: number){
        var ppgn = this.page_number + change;        
        this.page_Data(ppgn);
    }    
    last_Page(change: number){
        let lPage= Math.ceil(change/this.httpService.limit);
        this.page_Data(lPage);      
    }
    first_Page(change: number){
        this.page_Data(1);   
    }

    change_limit(e){
        // console.log(this.offset,this.limit,  1411);
        this.httpService.limit = Number($(e.target).val());
        this.httpService.offset = 0;
        this.page_number = 1;
        this.all_pages();
        this.reload_data.emit();
        // console.log(this.offset,this.limit, 1411);
    }

    on_paged_data(){
        // console.log(43443);
        this.all_pages();
    }

    ngOnInit() {
        window['wait_or_execute'];
        if(this.httpService.make_pages_when_loaded)
        {
            this.httpService.make_pages_when_loaded = false;
            this.all_pages();
        }
    }
}

