import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute, Router } from "@angular/router";
import {SocketService} from "../../app/socket.service";
import {HttpService} from "../../app/http.service";
import {Location} from '@angular/common';

declare var $: any;

@Component({
    selector: 'app-document',
    templateUrl: './document.component.html'
})
export class DocumentComponent implements OnInit {
    page_num = 1;
    doc_data: any;
    breadcrumb: any;  
    total_pages = 0;
    annot_hidden = false;
    mentionConfig = {};
    mention_list = [];
    should_save = false;
    socketService : SocketService
    constructor(private route: ActivatedRoute,
				private ss:SocketService,
                private httpService: HttpService,
                private router: Router,
                private _location: Location) 
    {
        let obj_this = this;
        obj_this.mention_list = []
        window['should_save'] = true;
        obj_this.socketService = ss;        
        obj_this.route.params.subscribe(params => {                        
            if(obj_this.router.url != obj_this.loaded_doc_path)
            {
                obj_this.loaded_doc_path = obj_this.router.url;
                obj_this.loadDoc();
            }
        });        
    }
    loaded_doc_path = undefined;

	hint() {
		$('.search-bar-container .search-hint-text').css("display", "none").fadeIn(700);
	}
	unhint() {
		$('.search-bar-container .search-hint-text').hide();
	}

	toggleAnnotations(){
		this.annot_hidden = !this.annot_hidden;
		window['show_annotation'] = !window['show_annotation']
		$('.topbar:first .annotation-buttons-container').toggle();
		$('.annotationLayer').toggle();
	}

    go_to_parent_url()
    {
        var obj_this = this;
        var parent_url = localStorage.getItem('previous_url');
        var curl = window['pathname'];
        if(parent_url.endsWith('login'))
        {
            parent_url = '/#/';
        }
        else if(parent_url)
        {
            obj_this.router.navigate([parent_url]);
        }
    }

    go_back()
    {
        this._location.back();
    }
    loadDoc(){
        console.log(window['dt_functions'].now_full(), 'doc started');
        var obj_this = this;
		window['show_annotation'] = false;
        window['functions'].showLoader('Document Data');        
        obj_this.onLibsLoaded();
    }

    placeCursorAtEnd() {
        let contentEditableElement = $('.active-mention')[0];
        var range,selection;
        if(document.createRange)//Firefox, Chrome, Opera, Safari, IE 9+
        {
            range = document.createRange();//Create a range (a range is a like the selection but invisible)
            range.selectNodeContents(contentEditableElement);//Select the entire contents of the element with the range
            range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
            selection = window.getSelection();//get the selection object (allows you to change selection)
            selection.removeAllRanges();//remove any selections already made
            selection.addRange(range);//make the range you have just created the visible selection
        }
    }


    doc_models = {

    }
    
    onLibsLoaded()
    {
        var obj_this = this;        
        var doc_type = obj_this.route.snapshot.params.doc_type;        
        let doc_id = obj_this.route.snapshot.params.res_id;
        let point_id = undefined;
        var is_dev_host = window.location.toString().indexOf('4200') > -1;
        is_dev_host = true;
        let args = {
            app: 'documents',
            model: 'File',
            // method: 'get_binary'
            method: 'get_file_data'
        }
        if(doc_type == 'meeting' || doc_type == 'topic')
        {
            args = {
                app: 'documents',
                model: 'AnnotationDocument',
                method: 'get_data'
            }
            obj_this.annotation_doc = true;
        }
        var input_data = {            
            args: args,
            params: {
                id : doc_id,
                data_url: is_dev_host
            }
        };                

        if(obj_this.route.toString().indexOf('discussion') > -1)
        {
            point_id = doc_id;
            input_data = {            
                args: args,
                params: {
                    id : doc_id,
                    data_url: is_dev_host
                }
            }; 
        }
        if(doc_type == 'meeting' || doc_type == 'topic'){
            var doc_name = doc_type + '-' + doc_id + '-' + obj_this.socketService.user_data.id + '.pdf';
            input_data.params['doc_id'] = doc_name;
        }
        // console.log(input_data, doc_type);
        var renderDoc = function(data){
            // console.log(data, Date(),  'doc data downloaded');
            data.file_type = doc_type;
            obj_this.doc_data = data;
            if (data.breadcrumb)
            {
                obj_this.breadcrumb = JSON.stringify(data.breadcrumb);
            }
            if(data.mention_list)
            {
                obj_this.mention_list = data.mention_list.filter(function(obj){
                    return obj.id != obj_this.socketService.user_data.id;
                });
                // console.log(obj_this.mention_list);
                obj_this.mentionConfig = {
                    items: obj_this.mention_list,
                    insertHTML: true,
                    triggerChar: "@",
                    dropUp: true,
                    labelKey: 'name',
                    mentionSelect: function(val){
                        let el = $('.active-mention');                
                        let tag = $('<a class="mention" mentioned_id="'+val.id+'" href="/#/'+val.group+'/'+val.id+'">'+val.name+'</a>');
                        el.append(tag);
                        let inputValue = el.html();
                        let secondString = inputValue.substring(inputValue.lastIndexOf('@'), inputValue.length-1);
                        let replaceValue = secondString.substring(0, secondString.indexOf('<'));
                        el.html(el.html().replace(replaceValue, ''));
                        obj_this.placeCursorAtEnd();
                        window['should_save'] = false;
                        return '';
                    }
                };
            }
            
            var doc_data = data;
            data.first_time = 1;
            data.type = doc_type;
            if(data.url)
            {
                doc_data['url'] = data.url;
            }
            else
            {
                doc_data['doc'] = data.doc;
            }
            if (data.excel){
                $('app-document .excel_doc').append(data.doc).show()
                $('.loadingoverlay').hide();
            }
            else{
                // console.log(window['dt_functions'].now_full(), 'doc info fetched');
                window['app_libs']['pdf'].load(function(){                    
                    window['pdf_js_module'].pdf_render(doc_data);
                });
            }            
        };
        if(!doc_type){
            //console.log("No doc_type");
            return;
        }
        
        obj_this.httpService.get(input_data, renderDoc, function(er){            
            window['pdf_js_module'].pdf_render(er);
        });
    }

    annotation_doc = false;

    on_page_changed(pageToMove)
    {                
        this.page_num = pageToMove;        
    }
    
    programatic_scroll = false;
    next_prev_page(pageToMove){        
        // console.log(pageToMove, 4343);
        pageToMove = parseInt(this.page_num+ '') + parseInt(pageToMove);
        // console.log(pageToMove, 3232);
        this.change_page(pageToMove);
    }

    change_page(pageToMove = null)
    {
        if(pageToMove == 0)
        {
            return;
        }
        if(pageToMove && pageToMove < 1)
        {            
            return;
        }
        if(!this.total_pages)
        {
            this.total_pages = $('.page-count:first').html();
        }
        if(pageToMove && pageToMove > this.total_pages)
        {            
            return;
        }
        try{
            if(pageToMove == 0)
            {
                pageToMove = this.total_pages;
            }
            if(!pageToMove)
            {
                pageToMove = this.page_num;
            }
            let test = parseInt(pageToMove);
            if(pageToMove > this.total_pages)
            {
                pageToMove = 1;
            }
            // console.log(pageToMove, 344);
            var temp = $('.pdfViewer>.page').eq(pageToMove-1);
            temp = temp.position().top;
            temp = temp + $('.PdfViewerWrapper').scrollTop();
            let pdf_scroll = temp - 5;
            this.programatic_scroll = true;
            this.page_num = pageToMove;
            $('.PdfViewerWrapper:first').scrollTop(pdf_scroll);
        }
        catch
        {
            this.page_num = 1;
        }
    }
    
    ngOnInit() {
        var obj_this = this;
        window['app_libs']['pdf'].load(function(){            
            $('.PdfViewerWrapper:first').scroll(function() {
                if(!this.total_pages)
                {
                    this.total_pages = $('.page-count:first').html();
                }
                if(obj_this.programatic_scroll)
                {
                    obj_this.programatic_scroll = false;
                    return;
                }
                var pdf_scroll = $(this).scrollTop();
                if(pdf_scroll == 0 )
                {
                    pdf_scroll = 1;
                }
                let page_height = $('.pdfViewer .page:first').height();
                obj_this.page_num = Math.ceil(pdf_scroll / page_height);
            });
        });
        $('#toggle-tools').click(function(){
            $('#ToolBarWrapper').toggle();
        });
    }
}