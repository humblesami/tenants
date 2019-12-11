import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpService } from '../../app/http.service';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { SocketService } from 'src/app/socket.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ProfileeditComponent } from '../profileedit/profileedit.component';
declare var $:any;

@Component({
	styleUrls:['./profiledetails.css'],
	templateUrl: 'profiledetails.component.html',
})
export class ProfileDetailsComponent implements OnInit {
	edit_mode = false;
	my_profile = false;
	last_login = {
		last: {
			login_time: '',
			platform: '',
			browser: '',
			ip: '',
			location: ''
		},
		second_last: {
			login_time: '',
			platform: '',
			browser: '',
			ip: '',
			location: ''
		}
	};
	profile_data = undefined;
	choice_fields = {};
	modified_profile_data = {};
	submitted = false;
	admin_info = false;
	next = '';
	prev = '';
	base_url = '';
	type = '';
	type_breadCrumb = '';
	socketService : SocketService;

	constructor(private httpService: HttpService, private formBuilder: FormBuilder, 
        private route: ActivatedRoute, private sanitizer: DomSanitizer,
    private ss: SocketService, private modalService: NgbModal) {
        this.edit_mode = false;
        this.profile_data = {};
        this.profile_data.login = this.last_login;  
        this.socketService = this.ss;      
		this.route.params.subscribe(params => this.get_data());
		// window['app_libs']['zebra'].load();
    }
    on_file_drop(container, file_object){
        let obj_this = this;
        let cls = $(container).attr('holdertype');        
        if(obj_this.profile_data[cls])
        {
            obj_this.profile_data[cls] = file_object.data;
            obj_this.modified_profile_data[cls] = file_object.data;
        }
	}

	open(section) {
        let obj_this = this;
		const modalRef = this.modalService.open(ProfileeditComponent, { keyboard: false, backdrop: 'static' });
		modalRef.componentInstance.edit_info = {
			section: section,
			user_id: this.route.snapshot.params.id
        }
        function on_modal_opened(a){
			obj_this.get_data();
        }
		modalRef.result.then(on_modal_opened, () => { })
	}

	edit_personal_info()
	{
		let config = {
			on_load: function(){
				$(document).ready(function(){
					$('#appModal .modal-body').html(
						`
						<div class="row label-control-form">
							<div class="container">
								<div class="row">
									<label for="name">
										<b>First Name</b>
									</label>
									<input type="text" placeholder="Enter First Name" id="first_name">
										<label for="name">
											<b>Last Name</b>
										</label>
									<input type="text" placeholder="Enter Last Name" id="last_name">
									<label for="c-phone">
										<b>Cell Phone</b>
									</label>
									<input type="text" placeholder="Enter Cell Phone" id="c-phone" required>
									<label for="email">
										<b>Email</b>
									</label>
									<input type="text" placeholder="Enter Email" id="email">
									<label for="location">
											<b>Location</b>
										</label>
					
									<input type="text" placeholder="Enter Location" id="location">
								</div>
							</div>
						</div>
						`
						);
				});
			},
			on_save:function(){

			}
		}
		window['init_popup'](config);
	}

	addFile(event, filter){
		const obj_this = this;
		var element = event.target;
		// console.log(element)
		var file = element.files[0];
		var fileReader = new FileReader();
		fileReader.readAsDataURL(file);
		fileReader.onload = function () {
			if(filter === 'profile'){
				obj_this.profile_data['image'] = fileReader.result;
				obj_this.modified_profile_data['image'] = fileReader.result;
			}
			else if(filter === 'admin'){
				obj_this.profile_data['admin_image'] = fileReader.result;
				obj_this.modified_profile_data['admin_image'] = fileReader.result;
			}
			else{
				obj_this.modified_profile_data['resume'] = fileReader.result;
			}
			obj_this.resumeUpload()
		};
		fileReader.onerror = function (error) {
			console.log('Error: ', error);
		};
	}
	update_image()
	{
		$('.update_image:first').click();
	}
	update_sign(){
		let obj_this = this;
        let sign_config = {
            signature_data: obj_this.profile_data.signature_data,            
            on_signed: function(signature_data) {
                obj_this.profile_data.signature_data = signature_data;
                obj_this.httpService.post({
                    args: {
                        app: 'meetings',
                        model: 'Profile',
                        method: 'save_signature',
                        post: 1,
                    },
                    params: {
                        signature_data: signature_data
                    }
                }, null, function(){

                });
            }            
		}
		window['app_libs']['signature'].load(()=>{
			window['init_sign'](sign_config);
		});
	}
	resumeUpload() {
		this.submitted = true;
		const obj_this = this;
		const form_data = obj_this.modified_profile_data;
		const input_data = {};
		for (const key in form_data) {
			if(obj_this.modified_profile_data[key] != '')
				input_data[key] = obj_this.modified_profile_data[key];			
		}
		input_data['user_id'] = obj_this.route.snapshot.params.id;
        let args = {
            app: 'meetings',
            model: 'Profile',
			method: 'update_profile',
			post: 1,
        }
        let final_input_data = {
            params: input_data,
            args: args
        };
		this.httpService.post(final_input_data,
			(data: any) => {
				obj_this.get_data();
			},
			(error) => {
                const x = document.getElementById('slot-select-error');
                if(x)
                {
                    x.className = 'snackbar-error show';
                    setTimeout(function () {
                        x.className = x.className.replace('show', '');
                    }, 3000);   
                }
				
            });
    }

	
	// add_resume(){
	// 	$('.add_resume').trigger('click');
	// }

	bio_html = undefined;
	get_data() {
		const obj_this = this;
		let id = undefined;
		let params = obj_this.route.snapshot.params;
		if(params.id)
		{
			id = params.id;
		}
        let input_data = undefined;
        if (id == obj_this.socketService.user_data.id || id == undefined) {
			obj_this.my_profile = true;	
		}
		input_data =
		{ 
			id: id,
			type:this.type
		};
		let args = {
            app: 'meetings',
            model: 'Profile',
            method: 'get_details'
        }			
        input_data = {
            params: input_data,
            args: args
        }; 
			
		const success_cb = function (result) {	
			obj_this.base_url = window['site_config'].server_base_url;		
			if(result.profile.admin_email || result.profile.admin_cell_phone
				|| result.profile.admin_fax || result.profile.admin_work_phone
				|| result.profile.admin_image || result.profile.admin_first_name
				|| result.profile.admin_last_name || result.profile.admin_nick_name
			)
			{
				obj_this.admin_info = true;
			}			
            // console.log(result);
            if(result.choice_fields)
            {
                obj_this.choice_fields = result.choice_fields;            
            }
            obj_this.profile_data['resume'] = null;
			for(var key in result.profile){
				obj_this.profile_data[key] = result.profile[key];
			}
			if(result.profile.image)
            {
                result.profile.image = obj_this.base_url + result.profile.image;
			}
			if(result.profile.bio)
			{
				obj_this.bio_html = obj_this.sanitizer.bypassSecurityTrustHtml(result.profile.bio);				
			}
			if (!obj_this.type_breadCrumb && result.profile.group)
			{
				obj_this.type = result.profile.group.toLowerCase()
				obj_this.type_breadCrumb = obj_this.type;
				if (obj_this.type_breadCrumb != 'staff')
				{
					obj_this.type_breadCrumb = obj_this.type_breadCrumb +'s';
				}
            }
            // console.log(obj_this.profile_data, 188);
		};
		const failure_cb = function (error) {
		};
		this.httpService.get(input_data, success_cb, failure_cb);
	}
	
	change_image()
	{
		let obj_this = this;
		let config = {
			hide_on_save: true,
			on_load: function(){
				$(document).ready(function(){
					$('#appModal .modal-body').html(
						`
						<input type="file" 
							accept=".jpg,.jpeg,.png" 
							name="profile_image_upload", id="profile_image_upload"/>
						`
						);
					setTimeout(() => {
						var file_input = $('#profile_image_upload');
						file_input.attr('dragdrop', 1);
						file_input.attr('input_type', 'image');
						window['apply_drag_drop'](file_input, null, function(data){
							try{
								let file = [];
								file.push(data.file);
								let resInfo = {
									res_app: 'meetings',
									res_model: 'Profile',
									res_id: obj_this.profile_data.id,
									res_field: 'image',
									file_type: data.file_type
								}
								window['upload_single_file'](file, resInfo, data.cloud, (data)=>{									
									obj_this.profile_data.image = data[0].image_url;
									if(obj_this.my_profile)
									{
										var user_cookie = localStorage.getItem('user');                
										let cuser = undefined;
										if(user_cookie)
										{
											cuser = JSON.parse(user_cookie);
										}
										if (cuser)
										{
											cuser.photo = obj_this.profile_data.image;
											cuser.user_photo = obj_this.profile_data.image;
											obj_this.socketService.user_data.photo = obj_this.profile_data.image;
											obj_this.socketService.user_photo = obj_this.base_url + obj_this.profile_data.image;
											let value = JSON.stringify(cuser);
											localStorage.setItem('user', value);
										}
									}
									$(".feedback-message").append('<p id="success-message" class="alert-success">File Uploaded Successfully </p>').fadeIn("slow");
								});
								
							}
							catch(er){
								console.log(er, 5455);
							}
						});
					}, 100);
				});
			},
			on_save:function(){

			}
		}
		window['init_popup'](config);
	}
	
	
	change_admin_image()
	{
		let obj_this = this;
		let config = {
			hide_on_save: true,
			on_load: function(){
				$(document).ready(function(){
					$('#appModal .modal-body').html(
						`
						<input type="file" 
							accept=".jpg,.jpeg,.png" 
							name="profile_image_upload", id="profile_image_upload"/>
						`
						);
					setTimeout(() => {
						var file_input = $('#profile_image_upload');
						file_input.attr('dragdrop', 1);
						file_input.attr('input_type', 'image');
						window['apply_drag_drop'](file_input, null, function(data){
							try{
								let file = [];
								file.push(data.file);
								let resInfo = {
									res_app: 'meetings',
									res_model: 'Profile',
									res_id: obj_this.profile_data.id,
									res_field: 'admin_image',
									file_type: data.file_type
								}
								window['upload_single_file'](file, resInfo, data.cloud, (data)=>{
									if(obj_this.my_profile || obj_this.socketService.admin_mode)
									{
										obj_this.profile_data.admin_image = data[0].image_url;
                                    }
                                    var success_message = '<p id="success-message" class="alert-success">File Uploaded Successfully </p>';
									$(".feedback-message").append(success_message).fadeIn("slow");
								});
								
							}
							catch(er){
								console.log(er, 5455);
							}
						});
					}, 100);
				});
			},
			on_save:function(){

			}
		}
		window['init_popup'](config);
	}

    init_sign()
    {
        let obj_this = this;
        let sign_config = {
            signature_data: obj_this.profile_data.signature_data,            
            on_signed: function(signature_data){
                obj_this.profile_data.signature_data = signature_data;
                obj_this.httpService.post({
                    args: {
                        app: 'meetings',
                        model: 'Profile',
                        method: 'save_signature',
                        post: 1,
                    },
                    params: {
						signature_data: signature_data,
						user_id: obj_this.route.snapshot.params.id
                    }
                }, null, function(){

                });
            }
		}
		window['app_libs']['signature'].load(()=>{
			window['init_sign'](sign_config);
		});
	}

	ngOnInit(){
		
	}

	ngOnChanges(){
        console.log("ngOnChanges")
	}
	ngDoCheck(){
		
	}
	
}
