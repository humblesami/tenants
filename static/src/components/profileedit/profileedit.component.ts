import { Component, OnInit, Input } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpService } from '../../app/http.service';
import { ActivatedRoute,Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { SocketService } from 'src/app/socket.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
declare var $:any;

@Component({
    selector: 'app-profileedit',
    templateUrl: './profileedit.component.html',
	styleUrls: ['./profileedit.component.css'],
})
export class ProfileeditComponent implements OnInit {
	@Input() public edit_info;
    edit_mode = true;
	my_profile = false;
	selectedEthnicity = [];
	section = '';
	delete_confirm = false;
	mobile_verification_code = undefined;
	user_id = undefined;
	selectedGender = [];
	selectedVeteran = [];
	selectedDisability = [];
	selectedTwoFactorAuth = [];
	selectedGroups = [];
	selectedCommittees;
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
		private router: Router,
		private ss: SocketService,public activeModal: NgbActiveModal) {
        this.profile_data = {};
        this.profile_data.login = this.last_login;  
		this.socketService = this.ss;      
		// window['app_libs']['zebra'].load(function(){
			
		// });
        // this.route.params.subscribe(params => this.get_data());
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
	input_date_format(){
		
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
				obj_this.profile_data['resume'] = fileReader.result;
			}
			obj_this.resumeUpload()
		};
		fileReader.onerror = function (error) {
			console.log('Error: ', error);
		};
	}
	resume_drag_drop = false;
	bio_html = undefined;
	get_data() {
		const obj_this = this;		
		let id = obj_this.edit_info.user_id;
        let input_data = undefined;
        if (id == obj_this.socketService.user_data.id || id == undefined) {
			obj_this.my_profile = true;	
		}
		input_data =
		{ 
			id: id,
			type:this.type,
			field_group: obj_this.section
		};
		let args = {
            app: 'meetings',
            model: 'Profile',
            method: 'get_update_profile_details'
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
            if(result.choice_fields)
			{
                obj_this.choice_fields = result.choice_fields;
            }
            
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
			if(result.profile.groups)
			{
				obj_this.selectedGroups = result.profile.groups;
			}
			if (result.profile.ethnicity.id)
			{
				obj_this.selectedEthnicity = result.profile.ethnicity;
			}
			if (result.profile.veteran.id)
			{
				obj_this.selectedVeteran = result.profile.veteran;
			}
			if (result.profile.gender.id)
			{
				obj_this.selectedGender = result.profile.gender;
			}
			if (result.profile.disability.id)
			{
				obj_this.selectedDisability = result.profile.disability;
			}
			if (result.profile.committees)
			{
				obj_this.selectedCommittees = result.profile.committees;
			}
			if (result.profile.two_factor_auth.id)
			{
				obj_this.selectedTwoFactorAuth = result.profile.two_factor_auth;
			}
			if (result.profile.mail_to_assistant)
			{
				$('#mail-to-assistant').prop('checked', true)
			}
			else
			{
				$('#mail-to-assistant').prop('checked', false)
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
			if(obj_this.resume_drag_drop)
			{
				return ;
			}
			var old_date_val = '';
			var picker_options = {
				dateFormat: "yy-mm-dd",
				changeMonth: true,
				changeYear: true,
				showButtonPanel: true,
				stepMonths: 12,
				
				onSelect: function(dateText) {
					$(this).change();
				}			
			}
			$('.profile-edit-container:first input.date').datepicker(picker_options)
			
			
			.focus(function(){
				old_date_val = this.value;
			})
			.on("change", function(dateText) {
				if(!this.value && !this.required)
				{
					obj_this.modified_profile_data[this.name] = '';
					return;
				}
				var is_valid = false;
				if(this.value)
				{
					var d = new Date(this.value);
					var day = d.getDate();
					var is_valid = !isNaN(d.getDate());
					var ar = this.value.split('-');
					// console.log(ar);
					if (day == ar[ar.length - 1])
					{
						is_valid = true;
					}
					else{
						is_valid = false;
					}
				}
				if (!is_valid){
					var error_label = $('<label class="alert-danger p-2">Given date '+ this.value+' is invalid</label>');
					$(this).before(error_label);
					error_label.delay(3000).fadeOut(500);
					this.value = old_date_val;
				}
				else{
					obj_this.modified_profile_data[this.name] = this.value;
				}
			});

			obj_this.resume_drag_drop = true;
			var file_input = $('input[name="add_resume"]');
			file_input.attr('dragdrop', 1);
			window['apply_drag_drop'](file_input, null, function(data){
				try{
					let file = []
					file.push(data.file)
					let resInfo = {
						res_app: 'meetings',
						res_model: 'Profile',
						res_id: obj_this.profile_data.id,
						res_field: 'resume',
						file_type: data.file_type
					}
					window['upload_single_file'](file, resInfo, data.cloud, (data)=>{
						obj_this.profile_data.resume = data[0];
						$(".feedback-message").append('<p id="success-message" class="alert-success">File Uploaded Successfully </p>').fadeIn("slow");
					});
					// obj_this.upload_files(file, data.cloud, (data)=>{
					// 	obj_this.profile_data.resume = data[0];
					// 	$(".feedback-message").append('<p id="success-message" class="alert-success">File Uploaded Successfully </p>').fadeIn("slow");
					// });
				}
				catch(er){
					console.log(er, 5455);
				}
			});
		};
		const failure_cb = function (error) {
		};
		this.httpService.get(input_data, success_cb, failure_cb);
	}

	resInfo = {};

	// upload_single_file(files, cloud=false, success)
    // {
	// 	let obj_this = this;
    //     // console.log(files, 13);
    //     for(var obj of files){
    //         if(!obj.file_name)
    //         {
    //             obj.file_name = obj.name;
    //         }
    //     }

    //     $('.file-drop-zone-title').addClass('loading').html('Uploading '+files.length+' files...');
    //     var url = window['site_config'].server_base_url+'/docs/upload-single-file';
    //     var formData = new FormData();
    //     if(!cloud)
    //     {
    //         var i= 0;
    //         for(var file of files){
    //             formData.append('file['+i+']', file);
    //             i++;
    //         }
    //     }
    //     else
    //     {
    //         formData.append('cloud_data', JSON.stringify(files));
    //     }
        
    //     formData.append('res_app', 'meetings');
    //     formData.append('res_model', 'Profile');
	// 	formData.append('res_id', obj_this.profile_data.id);
	// 	formData.append('file_field', 'resume');
	// 	let user: any;
    //     user = localStorage.getItem('user');
    //     user = JSON.parse(user);
    //     let headers = {'Authorization': 'Token '+user.token};
    //     var file_input_picker = $('.file-input-picker-container')
    //     // js_utils.addLoader(file_input_picker);
    //     // console.log(formData);
    //     $.ajax({
    //         url: url,
    //         data: formData,
    //         type: 'POST',            
    //         // dataType: 'JSON',
    //         headers: headers,
    //         contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
    //         processData: false, // NEEDED, DON'T OMIT THIS
    //         success: function(data){
    //             try{
    //                 success(data = JSON.parse(data));
    //             }
    //             catch(er){
    //                 console.log(data);
    //                 $(".feedback-message").append('<p id="success-message" class="alert-danger">Invalid data from file save</p>');
    //                 return;
    //             }
                
    //         },
    //         error: function(a,b,c,d){
    //             $('.feedback-message').append('<p id="success-message" class="alert-danger">Fail to Upload Files </p>').fadeIn("slow");
    //         },
    //         complete:function(){
    //             // js_utils.removeLoader(file_input_picker);
    //             $('.file-drop-zone-title').removeClass('loading').html('Drag & drop files here …');                
    //             setTimeout(function(){
    //                 $(".feedback-message").fadeOut("slow");
    //                 $(".feedback-message").html('');
    //             }, 4000);
    //         }
    //     });
    // }

	mail_to_assistant_change(value)
	{
		let obj_this = this;
		let mail_to_assistant = $('#mail-to-assistant').prop('checked');
		obj_this.modified_profile_data['mail_to_assistant'] = mail_to_assistant;		
	}

	update_image()
	{
		$('.update_image:first').click();
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
	
	mobile_phone_change(val)
	{
		this.modified_profile_data['mobile_verified'] = false;
		this.modified_profile_data['mobile_phone'] = val;
		this.profile_data.mobile_phone = val;
		this.profile_data.mobile_verified = false;
		this.setting_two_factor_auth();
	}

	onSubmit() {
		this.submitted = true;
		const obj_this = this;
		const form_data = obj_this.modified_profile_data;
		const input_data = {};
		for (const key in form_data) {
			if(obj_this.profile_data[key] || obj_this.modified_profile_data[key])
            {
                input_data[key] = obj_this.modified_profile_data[key];
            }
		}
		if (input_data['resume'] == 'removed')
		{
			input_data['resume'] = null;
		}
		input_data['user_id'] = obj_this.user_id;
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
                let obj_this = this;
                
                if(obj_this.my_profile)
                {
                    let profile = data.profile_data;
                    var user_cookie = localStorage.getItem('user');                
                    let cuser = undefined;
                    if(user_cookie)
                    {
                        cuser = JSON.parse(user_cookie);
                    }
                    if (cuser)
                    {
                        profile.token = cuser.token;
                        profile.user_photo = profile.photo;
                        obj_this.socketService.user_data.groups = profile.groups;
                        obj_this.socketService.user_data.name = profile.name;
                        obj_this.socketService.user_data.photo = profile.photo;
                        obj_this.socketService.user_photo = obj_this.base_url + profile.photo;
                        let value = JSON.stringify(profile);
                        localStorage.setItem('user', value);

                        console.log(obj_this.socketService.user_photo, 133);
                    }
                }				
                
				// obj_this.router.navigate(['/my-profile']);
				obj_this.activeModal.close('saved')
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
	delete_confirmed()
	{
		this.modified_profile_data['resume'] = 'removed';
		this.profile_data['resume'] = null;
		this.delete_confirm = false;
	}
	delete_cancelled()
	{
		this.delete_confirm = false;
	}
	
	add_resume(){
		$('.add_resume').trigger('click');
	}
	edit_resume(e){
		let obj_this = this;
		if ($(e).hasClass('fa-trash-alt'))
		{
			obj_this.delete_confirm = true;
			return;
		}
		$('.edit_resume').trigger('click');
    }
    onCancel(){
        this.activeModal.close();
    }


    init_sign()
    {
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
	setEthnicity()
	{
        if(!this.selectedEthnicity)
        {
            this.modified_profile_data['ethnicity'] = null;
        }
        else
        {
            this.modified_profile_data['ethnicity'] = this.selectedEthnicity['id'];
        }
	}
	setGender()
	{
        if(!this.selectedGender)
        {
            this.modified_profile_data['gender'] = null;
        }
		else{
            this.modified_profile_data['gender'] = this.selectedGender['id'];
        }
	}
	setVeteran()
	{
        if(!this.selectedVeteran)
        {
            this.modified_profile_data['veteran'] = null;
        }
		else{
            this.modified_profile_data['veteran'] = this.selectedVeteran['id'];
        }
	}
	setDisability()
	{
        if(!this.selectedDisability)
        {
            this.modified_profile_data['disability'] = null;
        }
		else{
            this.modified_profile_data['disability'] = this.selectedDisability['id'];
        }
	}
	setGroups()
	{
        if (this.selectedGroups.length)
        {
            this.modified_profile_data['groups'] = this.selectedGroups;
        }
        else
        {
            this.modified_profile_data['groups'] = null;
        }
    }
	setCommittees()
	{
        if (this.selectedCommittees.length)
        {
            this.modified_profile_data['committees'] = this.selectedCommittees;
        }
        else
        {
            this.modified_profile_data['committees'] = 'removed_all';
        }
    }
    verification_id: string;

	setting_two_factor_auth()
	{
		let obj_this = this;
		if(!obj_this.profile_data.mobile_phone && !obj_this.modified_profile_data['mobile_phone'])
		{
			$('#c-phone').focus();
			obj_this.selectedTwoFactorAuth = [];
			return;
		}
		obj_this.two_factor_auth_popup_config();
		let args = {
			app: 'authsignup',
			model: 'AuthUser',
			method: 'send_mobile_verfication_code'
		}
		let user_mobile_phone = '';
		if (obj_this.profile_data.mobile_phone)
		{
			user_mobile_phone = obj_this.profile_data.mobile_phone;
		}
		else
		{
			user_mobile_phone = obj_this.modified_profile_data['mobile_phone'];
		}
		let final_input_data = {
			params: {mobile_phone: user_mobile_phone},
			args: args
        }
		obj_this.httpService.get(final_input_data,function(data){            
			obj_this.verification_id = data.uuid;
			obj_this.profile_data.mobile_phone = user_mobile_phone;
			obj_this.modified_profile_data['mobile_phone'] = user_mobile_phone;
        }, null);		
	}

	two_factor_auth_popup_config()
	{
		let obj_this = this;
		let config = {
			on_load: function(){
				obj_this.load_verification_popup();
			},
			on_save:function(){						
				obj_this.mobile_verification_code = $('#verification_code').val();
				if(!obj_this.mobile_verification_code)
				{
					obj_this.selectedTwoFactorAuth = [];
					$('#code-error').show();
				}
				else
				{
					let input_data = {
						uuid: obj_this.verification_id,
						verification_code: obj_this.mobile_verification_code,
					}
					let args = {
						app: 'authsignup',
						model: 'AuthUser',
						method: 'authenticate_mobile'
					}
					let final_input_data = {
						params: input_data,
						args: args
					}
					obj_this.httpService.get(final_input_data, function(data){
						$('#code-error').hide();
						obj_this.modified_profile_data['two_factor_auth'] = obj_this.selectedTwoFactorAuth['id'];
						obj_this.modified_profile_data['mobile_verified'] = true;
						$('#appModal').modal('hide');
					},function(err){
						$('#code-error').show()
						$('#code-error').text(err);
					});
				}
			},
			on_close: function(){
				obj_this.selectedTwoFactorAuth = obj_this.profile_data.two_factor_auth;
				obj_this.selectedTwoFactorAuth = [];
			}
		}
		window['init_popup'](config);
	}

	setTowFactorAuth()
	{
		let obj_this = this;
		if (obj_this.selectedTwoFactorAuth)
        {
			if(!obj_this.profile_data.mobile_verified && obj_this.selectedTwoFactorAuth['name'].toLowerCase() == 'phone')
			{
				obj_this.setting_two_factor_auth();
			}
			else
			{
				this.modified_profile_data['two_factor_auth'] = obj_this.selectedTwoFactorAuth['id'];
			}
        }
        else
        {
            this.modified_profile_data['two_factor_auth'] = null;
        }
    }
    
    load_verification_popup(){
        setTimeout(function(){
            $('#appModal .modal-body').html(`
                <input type="text" name="verification_code" id="verification_code"
                placeholder="Please Enter Mobile Verification Code"
                class="form-control verification-code" required/>
                <small style="display: none;" id="code-error" class="text-danger">
                    You can not select tow factor authentication type phone untill you verify your phone number
                </small>
            `);
            $('#verification_code').keyup(function(e){
                if(e.keyCode == 13)
                {
                    $('#save-sig').click();
                }
                if(!$(this).val())
                {
                    $('#code-error').show()
                    $('#code-error').text('Please Provide a verification code.');
                }
                else
                {
                    $('#code-error').hide();
                }
            });
        }, 100)        
        
    }
	
	ngOnInit(){
		// console.log(this.edit_info, 134);
		
		
		if (this.edit_info)
		{
			this.section = this.edit_info.section;
			this.user_id = this.edit_info.user_id;
			this.get_data();
        }
	}	
}