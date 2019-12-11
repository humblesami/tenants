import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import {Location} from '@angular/common';
declare var $: any;

@Component({
    selector: 'app-recorddetails',
    templateUrl: './recorddetails.component.html',
    styleUrls: ['./recorddetails.css']
})
export class RecorddetailsComponent implements OnInit {
    id: any;
    url: any;
    model: any;
    constructor(private route: ActivatedRoute, private sanitizer: DomSanitizer, private _location: Location) { 
        window['functions'].showLoader('jangoiframe');
    }
    ngOnInit() {
        this.id= this.route.snapshot.params.id;
        this.model= this.route.snapshot.params.model;
        // let temp = window.location.hash.split("edit")[1]
        this.url = window['site_config'].server_base_url+"/" + this.model + "/" + this.id;
            
        this.url = this.sanitizer.bypassSecurityTrustResourceUrl(this.url)
        // $('html').css('overflow', 'hidden');
        try{
            $('#record_details_iframe').load(function(){
                window['functions'].hideLoader('jangoiframe')
            });
        }
        catch(er){
            console.log(er);
        }        
    }

    go_back(){
        this._location.back();
    }

    ngOnDestroy() {
        $('html').css('overflow', 'auto');
    }
}