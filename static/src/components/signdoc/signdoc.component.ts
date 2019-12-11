import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { ActivatedRoute } from '@angular/router';
declare var $: any;

@Component({
    selector: 'app-signdoc',
    templateUrl: './signdoc.component.html',
    styleUrls: ['./signdoc.component.css']
})
export class SigndocComponent implements OnInit {

    doc_name: any;
    constructor(private route: ActivatedRoute,private httpService: HttpService) { 
    }
    ngOnInit() {
        let obj_this = this;
        var doc_id = obj_this.route.snapshot.params.res_id;
        $('body').addClass('overflow-hide');
        window['functions'].showLoader('dociframe');
        $('#signdocframe').load(function(){
            $(this).show();
            window['functions'].hideLoader('dociframe');
        });
        let args = {
            app: 'esign',
            model: 'SignatureDoc',
            method: 'get_token'
        }			
        let final_input_data = {
            params: { doc_id: doc_id },
            args: args
        };
        obj_this.httpService.get(final_input_data, function(data){
            obj_this.doc_name = data.doc_name
            var path = window['site_config'].server_base_url +'/e_sign/sign/model=meeting_point.document&id='+doc_id+' &/'+data.token;
            $('#signdocframe').attr('src',path);
        }, undefined);
    }
    ngOnDestroy()
    {
        $('body').removeClass('overflow-hide');
    }
}
