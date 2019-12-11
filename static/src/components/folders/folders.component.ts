import { Component, OnInit, Input, Output, EventEmitter, NgZone } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { SocketService } from 'src/app/socket.service';
import { RenameService } from 'src/app/rename.service';
import { UserService } from 'src/app/user.service';
import { ActivatedRoute } from '@angular/router';
declare var $:any;

@Component({
    selector: 'app-folders',
    templateUrl: './folders.component.html',
    styleUrls: ['./folders.component.css']
})
export class FoldersComponent implements OnInit {
    @Input() search_kw = '';
    @Input() search_type = '';
    @Input() recursive : undefined;
    @Input() parent_id: number;
    parent;
    access_denied = false;
    records = [];
    message = '';
    parents = [];
    no_resource = false;
    new_folder = undefined;
    show_renamer_button = false;
    modified_folder_data =undefined;

    heading = 'Resources';
    bread_crumb = {
        items: [],
        title: ''
    };
    search_kw1 = '';
    httpService: HttpService;
    userService: UserService;
    renameService: RenameService;

    constructor(private httpServ: HttpService,
        private renameSer: RenameService,
        private userServ: UserService,
        private zone: NgZone,
        private route: ActivatedRoute,
        private socketService: SocketService) {
            let obj_this = this;
            obj_this.httpService = httpServ;
            obj_this.userService = userServ;
            obj_this.renameService = renameSer;
    }

    delete_folder(evn, folder_id, folder_total_files)
    {
        evn.stopPropagation();
        evn.preventDefault();
        let obj_this = this;
        if(folder_total_files){
            obj_this.message = 'Are you sure to delete? This folder contains '+ folder_total_files + ' file(s).';
        }else{
            obj_this.message = 'Are you sure to delete?';
        }

        window['bootbox'].confirm(obj_this.message , function(dr){
        if(!dr)
            {
                return;
            }
            let input_data = {
                folder_id: folder_id,
            }
            let args = {
                app: 'resources',
                model: 'Folder',
                method: 'delete_folder'
            }
            let final_input = {
                params: input_data,
                args: args
            }

            obj_this.httpService.get(final_input, (data)=>{
                obj_this.records =  obj_this.records.filter((el)=>{
                    return folder_id != el.id;
                });
            }, null);
        });
    }

    personal = false;

    get_list()
    {
        let obj_this = this;
        let args = {
            app: 'resources',
            model: 'Folder',
            method: 'search_folders'
        }
        let final_input_data = {
            params: {
                parent_id: obj_this.parent_id,
                recursive: obj_this.recursive,
                kw: obj_this.search_kw,
                folder_ids_to_move: obj_this.renameService.objects_to_move.folders,
                current_parent_id: obj_this.renameService.objects_to_move.current_parent_id
            },
            args: args
        };
        // console.log(final_input_data.params, 333);
        obj_this.httpService.get(final_input_data,
        (result: any) => {
            if(obj_this.renameService.objects_to_move.current_parent_id)
            {
                obj_this.can_be_parent = result.can_be_parent;                
            }            
            obj_this.on_result(result);
        },null);
    }
    can_be_parent = false;

    @Output() data_loaded: EventEmitter<any> = new EventEmitter();
    on_result(result){
        let obj_this = this;
        if (Object.entries(result).length === 0)
        {
            obj_this.access_denied = true;
            $('div.sub.search').hide();
            return;
        }
        obj_this.records = result.folders;        
        if(result.personal)
        {
            obj_this.personal = result.personal;
            obj_this.add_folder_create_button();
        }
        if(obj_this.parent_id)
        {
            obj_this.data_loaded.emit(result);
        }
        var reset_moving_objects = function(){
            // console.log(4343);
            obj_this.renameService.reset_moveable_values();
        }
        var do_paste = function(){
            obj_this.on_paste_clicked();
        }
        var load_preselected = function(){
            
            obj_this.renameService.load_movables(obj_this.parent_id, 'folder', result.can_be_parent);
            // console.log(obj_this.renameService.objects_to_move.current_parent_id, 777, obj_this.can_be_parent);
            if(obj_this.renameService.objects_to_move.current_parent_id && obj_this.can_be_parent)
            {
                var paste_button_html = '<button class="btn btn-primary paste"> Paste ';
                paste_button_html += '('+ (obj_this.renameService.objects_to_move.files.length+obj_this.renameService.objects_to_move.folders.length)+' items) Here';
                paste_button_html += '</button>';
                var paste_button = $(paste_button_html);
                var cancle_button_html = '<button class="btn btn-danger cancle_btn" id="cancle_btn">Cancle</button>'; 
                var cancle_button = $(cancle_button_html);
                cancle_button.click(reset_moving_objects);
                paste_button.click(do_paste);
                $('.breadcrumbSection .edit-buttons:first .paste .cancle_btn').remove();
                $('.breadcrumbSection .edit-buttons:first').prepend(paste_button,cancle_button);
            }
        }
        obj_this.records && obj_this.records.length > 0 ? obj_this.no_resource = false : obj_this.no_resource = true;
        if(obj_this.parent_id)
        {
            setTimeout(load_preselected, 200);
        }
    }

    create_folder_popup_config()
    {
        let obj_this = this;
        var folders = obj_this.records;
        // console.log(folders);
        let config = {
            on_load: function(){
                obj_this.load_create_folder_popup();
            },
            on_save:function(){
                obj_this.new_folder = $('#new_folder').val();
                if(!obj_this.new_folder)
                {
                    obj_this.new_folder = [];
                    $('#folder-error').show();
                }
                else
                {
                    obj_this.parent_id = obj_this.route.snapshot.params.id;
                    let input_data = {
                        name: obj_this.new_folder,
                        parent_id : obj_this.parent_id,
                    };

                    let args = {
                        app: 'resources',
                        model: 'Folder',
                        method: 'create_new'
                    }
                    let final_input_data = {
                        params: input_data,
                        args: args
                    }
                    // console.log(input_data, 323);
                    obj_this.httpService.get(final_input_data, function(data){
                        $('#folder-error').hide();
                        // console.log(data, 30006);
                        let temp = [];
                        for(var rec of folders)
                        {
                            temp.push({id: rec.id, name:rec.name , parent: rec.parent, personal: rec.personal});
                        }
                        temp.push(data);
                        // console.log(temp);
                        obj_this.records = temp;
                        // obj_this.zone.run(()=> {obj_this.records = temp;});
                    },function(err){
                        $('#folder-error').show()
                        $('#folder-error').text(err);
                    });
                }
            },
            hide:1,
        }
        window['init_popup'](config);
    }

    load_create_folder_popup(){
        $('#appModal .modal-body').html(`
            <input type="text" name="new_folder" id="new_folder"
            placeholder="Please Enter Folder Name"
            class="form-control new_folder" required/>
            <small style="display: none;" id="folder-error" class="text-danger">
                Enter a Valider Name
            </small>
        `);
        $('#new_folder').keyup(function(e){
            if(e.keyCode == 13)
            {
                $('#save-sig').click();
            }
            if(!$(this).val())
            {
                $('#folder-error').show();
                $('#folder-error').text('Enter Valid Name.');
            }
            else
            {
                $('#folder-error').hide();
            }
        });
        $('#appModal').modal('show');
    }

    add_folder_create_button(){
        $('#create_new_folder').remove();
        if(!this.socketService.admin_mode && !this.personal)
        {
            return;
        }
        let obj_this = this;
        // var create_button = $('<button class="btn btn-primary" >Create Folder</button>');
        var create_button = $('<div class="edit-buttons icons"><a id="create_new_folder" class="btn btn-primary"><i class="fa fa-plus"></i></a></div>');
        var on_create_click = function(){
            obj_this.create_folder_popup_config();
        }
        create_button.click(function(){
            on_create_click();
        });
        var edit_buttons = $('<div class="edit-buttons"></div>');
        $('.breadcrumbSection .edit-buttons:first').remove();
        $('.breadcrumbSection:first').append(edit_buttons);
        edit_buttons.append(create_button);        
    }

    on_paste_clicked(evn=undefined, folder_id=undefined, folder=undefined){
        let obj_this = this;
        if(evn)
        {
            evn.preventDefault();
            evn.stopPropagation();
        }
        let args = {
            app: 'resources',
            model: 'Folder',
            method: 'move_objects'
        }
        let final_input_data = {
            params: {
                folder_id: obj_this.parent_id,
                objects_to_move: obj_this.renameService.objects_to_move,
            },
            args: args
        };
        if(folder_id)
        {
            final_input_data.params.folder_id = folder_id;
        }
        // console.log(final_input_data.params, 333);
        obj_this.httpService.get(final_input_data,(result: any) => {
            obj_this.renameService.on_files_moved(result.files, evn);
            obj_this.renameService.on_folders_moved(result.folders, evn);
            if(folder){
                folder.total_files += result.files.length;
            }
            var cp_id = obj_this.renameService.objects_to_move.current_parent_id;
            var prev_parent = obj_this.records.find(function(el){
                return el.id == cp_id;
            });
            if(prev_parent)
            {            
                prev_parent.total_files -=  result.files.length;
            }
            obj_this.renameService.reset_moveable_values();
        }, null);        
    }
    
    ngOnInit() {
        let obj_this = this;        
        var on_folders_moved = function(data, evn){
            var object_ids = obj_this.renameService.objects_to_move.folders;
            if(evn)
            {
                obj_this.records = obj_this.records.filter(function(item){
                    return object_ids.indexOf(item.id) == -1
                });
            }
            else{
                obj_this.records = obj_this.records.concat(data);
            }                
            obj_this.renameService.objects_to_move.folders = [];
        }
        obj_this.renameService.on_folders_moved = on_folders_moved;        
        
        obj_this.add_folder_create_button();        
        // console.log(obj_this.search_kw, obj_this.search_type, obj_this.recursive);
        if(obj_this.search_type == 'files')
        {
            return;
        }
        obj_this.parent_id = obj_this.route.snapshot.params.id;
        if(obj_this.parent_id)
        {
            obj_this.parent = {
                app:'resources',
                model:'Folder',
                id: obj_this.parent_id
            }
        }
        this.get_list();
        obj_this.socketService.call_backs_on_mode_changed['handle_folder_create'] = function(){
            if(obj_this.socketService.admin_mode || obj_this.personal)
            {
                $('#create_new_folder').remove();
                obj_this.add_folder_create_button();
            }
            else{
                $('#create_new_folder').remove();
            }
        }
    }
    ngOnDestroy(){
        delete this.socketService.call_backs_on_mode_changed['handle_folder_create'];
    }
}
