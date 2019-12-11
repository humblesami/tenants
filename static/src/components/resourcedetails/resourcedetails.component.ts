import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SocketService } from 'src/app/socket.service';
declare var $:any;

@Component({
    selector: 'app-resourcedetails',
    styleUrls:['./resourcedetails.css'],
    templateUrl: 'resourcedetails.component.html'
})

export class ResourceDetailsComponent implements OnInit {
    folder_id = '';
    parents = [];
    folder : any;
    reloading = true;
    advance_search = false;
    search_options = undefined;
    cookie_key = 'resources/root/search';
    constructor(private route: ActivatedRoute, public socketService: SocketService){
        let obj_this = this;
        obj_this.seat_default_options();
        obj_this.advance_search_toggled(true);
        // console.log(obj_this.search_options, obj_this.cookie_key);
        obj_this.route.params.subscribe(params => {            
            obj_this.reloading = true;
            setTimeout(function(){
                // console.log(434);
                obj_this.folder_id = obj_this.route.snapshot.params.id;
                obj_this.reloading = false;
            }, 20);
        });        
    }
    data_loaded(data){
        this.folder = data;
        this.parents = data.parents;
    }

    advance_search_toggled(on_init=false){
        let obj_this = this;
        let is_not_root = obj_this.route.snapshot.params.id;
        if(obj_this.advance_search)
        {
            $('.resources .search_options:first').show();
            $('.bold-setting').addClass('text-primary').removeClass('text-muted small');            
        }
        else{
            $('.resources .search_options:first').hide();
            $('.bold-setting').addClass('text-muted small').removeClass('text-primary');
        }
    }

    seat_default_options(){
        let obj_this = this;
        let is_not_root = obj_this.route.snapshot.params.id;
        var prev_phrase = '';
        if(obj_this.search_options && obj_this.search_options.search_kw)
        {
            prev_phrase = obj_this.search_options.search_kw;
        }
        // console.log(prev_phrase, 4343);
        if(is_not_root)
        {            
            obj_this.search_options = {
                search_type : 'all',
                recursive : false,
                search_kw : prev_phrase,
            }
        }
        else{
            obj_this.search_options = {
                search_type : 'folders',
                recursive : false,
                search_kw : prev_phrase,
            }
        }
    }

    search(st=undefined){        
        let obj_this = this;
        if(st)
        {
            obj_this.search_options.search_type = st;
        }
        var word = $('#search_input').val();
        obj_this.search_options.search_kw = word;
        obj_this.reloading = true;
        if(!obj_this.advance_search)
        {
            obj_this.seat_default_options();
        }
        else if (obj_this.search_options.search_type)
        {
            if(obj_this.search_options.search_type == 'files' && obj_this.cookie_key.indexOf('root') > -1)
            {
                obj_this.search_options.recursive = true;
            }
            localStorage.setItem(obj_this.cookie_key, JSON.stringify(obj_this.search_options));
        }
        // console.log(obj_this.search_options.recursive, 444);
        setTimeout(function(){
            obj_this.folder_id = obj_this.route.snapshot.params.id;
            obj_this.reloading = false;
        }, 20);
    }

    
    ngOnInit() {
        let obj_this = this;
        // $('.search_options>input[values="'+obj_this.search_options.search_type+'"]').prop('checked', true);
        obj_this.folder_id = obj_this.route.snapshot.params.id;
        // console.log(43434);
        obj_this.search();
    }
}
