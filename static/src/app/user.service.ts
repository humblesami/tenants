import { Injectable } from '@angular/core';
import { HttpService } from './http.service';
import { SocketService } from './socket.service';
import { UserlistmodalComponent } from 'src/components/userlistmodal/userlistmodal.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ProfilesummaryComponent } from 'src/components/profilesummary/profilesummary.component';

declare var $: any

@Injectable()

export class UserService {
    server_url;
    
    constructor(private httpService:HttpService, private socketService: SocketService,
        private modalService: NgbModal) {
        
    }
    private users = [];
    selected_object;
    valid_users = [];
    selectedUsers = [];    

    set_users(list)
    {
        // console.log(list, 133);
        this.users = list;
    }

    show_profile_summary(profile_id){
        let obj_this = this;
        const modalRef = obj_this.modalService.open(ProfilesummaryComponent, { windowClass: 'user-summary-modal', keyboard: false});
        modalRef.componentInstance.user_id = profile_id;
        // console.log(profile_id, 8);
    }

    saveusers(selected_users){
        let obj_this = this;        
        var user_ids = [];        
        for(var user of selected_users)
        {
            user_ids.push(user.id);
        }
        let args = {
            app: 'my_admin',
            model: 'Helper',
            method: 'define_access'
        }
        let final_input_data = {
            params: {
                object_id : obj_this.selected_object.id,                
                model:obj_this.selected_object.model,
                app: obj_this.selected_object.app,                
                user_ids : user_ids,
            },
            args: args
        };
        obj_this.httpService.get(final_input_data,
        (result: any) => {
            console.log(result);           
        },null);
    }

    closemodel(){
        $('#select_user_modal').modal('hide');
        this.selectedUsers = [];
        this.selected_object  = undefined;
    }

    get_access_details(obj, app, model, parent=null){
        let obj_this = this;
        obj_this.selectedUsers = [];
        obj.model = model;
        obj.app = app;
        obj_this.selected_object = obj;
        
        let args = {
            app: 'my_admin',
            model: 'Helper',
            method: 'get_resource_audience'
        }
        let params = {
            object_id: obj.id,
            app: app,
            model: model,
            parent: parent
        };
        // console.log(params);
        let final_input_data = {
            params: params,
            args: args
        };

        var on_modal_closed = function(result){
            obj_this.saveusers(result);
        };

        obj_this.httpService.get(final_input_data,
        (result: any) => {
            
            if(parent && parent.id)
            {
                obj_this.valid_users = result.valid;
            }
            else{
                obj_this.valid_users = obj_this.users;
            }
            var valid_users = obj_this.valid_users;
            // console.log(obj_this.valid_users, 54);
            obj_this.selectedUsers = result.selected;
            // console.log(valid_users, 43434);
            let owner = false;
            if (!obj.personal)
            {
                if (obj.owner)
                {
                    owner = true
                }
            }
            else
            {
                owner = true
            }
            var diaolog_options = {
                selected_users: result.selected,
                user_list: valid_users,
                component: UserlistmodalComponent,
                extra_input: {},
                owner: owner,
                call_back: on_modal_closed, 
            };
            obj_this.socketService.user_selection_dialog(diaolog_options);
        },null);        
    }

    
}
