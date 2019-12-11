import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from "@angular/router";
import { HttpService } from "../../app/http.service";
import { SocketService } from "../../app/socket.service";
import { Router } from "@angular/router";
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { UserlistmodalComponent } from '../userlistmodal/userlistmodal.component';
declare var $:any;


@Component({
    styleUrls:['./esigndocdetails.css', '../meetings/meetings.css'],
    templateUrl: 'esigndocdetails.component.html'
})
export class EsignDocDetailsComponent implements OnInit {
    doc: any;
    doc_id:string;
    doc_name: any;
    add_users:boolean = false;
    selected_respondents:any = [];
    all_profile_users:any = [];
    is_public = false;
    users_list = [];
    sign_count = 0;
    all_users_list = [];
    selectedUser: any;
    socketService: SocketService;

    constructor(private httpService: HttpService,
        private route: ActivatedRoute,
        private ss: SocketService,
        private modalService: NgbModal,
        private router: Router) {
            window['app_libs']['pdf'].load();
        // this.route.params.subscribe(params => this.get_data());
        this.socketService = ss;
    }

    get_data() {

    }

    signature_required = false;

    setUserSelection(){
        let obj_this = this;
        if (obj_this.selectedUser)
        {
            let sign = $('.active_signature');
            sign.attr("user", obj_this.selectedUser['id']);
            sign.find('.user_name').remove();
            sign.append(`: <span class='user_name'>${obj_this.selectedUser['name']}</span>`);
        }
        $('#select_user_modal').modal('hide');
    }

    isAdmin = false;


    add_new_users()
    {
        let obj_this = this;
        var on_modal_closed = function(result){
            if (result)
            {
                let input_data = {
                    doc_id: obj_this.doc_id,
                    new_respondents: result
                }
                let args = {
                    app: 'esign',
                    model: 'SignatureDoc',
                    method: 'add_new_respondents'
                }
                let final_input = {
                    params: input_data,
                    args: args
                }
                obj_this.httpService.get(final_input, (data:any) =>{
                    obj_this.all_users_list = obj_this.users_list = obj_this.selected_respondents = result;
                }, null)
            }
        };


        var diaolog_options = {
            selected_users: obj_this.selected_respondents,
            user_list: [],
            component: UserlistmodalComponent,
            extra_input: {},
            call_back: on_modal_closed,
        };
        obj_this.socketService.user_selection_dialog(diaolog_options);
    }

    close_users_modal()
    {
        $('#select_user_modal').modal('hide');
    }

    meetings = [];
    signature_started = true;
    selectedMeeting: any;


    ngOnInit() {
        $('#fields-hide').click(function(){
            $(this).toggleClass("text-white");
            $('.doc-container.admin #doc-side-scroll').toggle();
        });
        var obj_this = this;
        var
            canvas,
            pdf_url,
            users,
            doc_data,
            send_to_all,
            meeting_id,
            req_url,

            ctx,
            pdfDoc,
            scale,
            pageNum,
            ajax_options,
            token = $('.sign_token').val() || ""

        if (!obj_this.doc_id) {
            var route_token = obj_this.route.snapshot.params.token;
            obj_this.doc_id = obj_this.route.snapshot.params.id;
            if (route_token)
            {
                token = obj_this.route.snapshot.params.token;
                obj_this.is_public = true;
            }
        }
        // console.log(doc_id, doc_data, 833, token);

        obj_this.doc = {
            "id": obj_this.doc_id,
            "doc_name": ''
        };
        // console.log(obj_this.socketService.user_data, 444);

        var page_zoom = 1;
        $(function(){
            $('#dropdown_meeting').val(meeting_id);
            // Go to previous page
            $("#prev").on('click', function goPrevious() {
                if (pageNum <= 1)
                    return;
                pageNum--;
                renderPage(pageNum);
            });

            // Go to next page
            $("#next").on('click', function goNext() {
                if (pageNum >= pdfDoc.numPages)
                    return;
                pageNum++;
                renderPage(pageNum);
            });



            $("#zoomIn").on('click', function zoomIn() {
                var scaleSelect = document.getElementById("scaleSelect") as HTMLSelectElement;
                var last = scaleSelect.options.length - 1;
                if (scaleSelect.selectedIndex < last) {
                    scale = scaleSelect.options[scaleSelect.selectedIndex + 1].value;
                    scaleSelect.selectedIndex += 1;
                    zoom_changed(scale);
                }
            });

            $("#zoomOut").on('click', function zoomOut() {
                var scaleSelect = document.getElementById("scaleSelect") as HTMLSelectElement;
                var last = scaleSelect.options.length - 1;
                if (scaleSelect.selectedIndex > 0) {
                    scale = scaleSelect.options[scaleSelect.selectedIndex - 1].value;
                    scaleSelect.selectedIndex -= 1;
                    zoom_changed(scale);
                }
            });

            $("#scaleSelect").on('click', function zoomSelect() {
                var scaleSelect = document.getElementById("scaleSelect") as HTMLSelectElement;
                scale = scaleSelect.options[scaleSelect.selectedIndex].value;
                zoom_changed(scale);
            });

            $('#check_box_send_all').change(function() {
                if ($("#check_box_send_all").is(':checked')) {
                    var signs_exist = false;
                    if($('#viewer_container .sign_container').length || $('#viewer_container .new_sign').length)
                    {
                        signs_exist = true;
                    }
                    if(signs_exist)
                    {
                        window['bootbox'].confirm('All assigned signatures will be removed', function(res){
                            if(res)
                            {
                                if($('.sign_container[signed="true"]').length > 0)
                                {
                                    console.log('Invalid activity');
                                    return;
                                }
                                $('.dragabl-fields').hide();
                                $('.new_sign,.sign_container').remove();
                                toggle_guide_btn(false, 'reset');
                                $('#save-doc-data').click();
                                $('#viewer_container .sign_container').remove();
                                $('#viewer_container .new_sign').remove();
                                save_attachemnt_to_meeting();
                            }
                            else{
                                $("#check_box_send_all").prop('checked', false);
                            }
                        })
                    }
                    else{
                        $('#save-doc-data').click();
                        save_attachemnt_to_meeting();
                        $('.dragabl-fields').hide();
                    }
                } else {
                    save_attachemnt_to_meeting();
                    $('.dragabl-fields').show();
                }
            })
            $('#dropdown_meeting').change(function() {
                if (!$('#dropdown_meeting').val()) {
                    obj_this.users_list = obj_this.all_users_list;
                    $('#check_box_send_all').removeAttr('checked');
                    // $('.check_box_send_all').hide();
                    $('.dragabl-fields').show();
                }
                save_attachemnt_to_meeting();
            });
            $('#select_user_modal').on('shown.bs.modal', function () {
                var sign = $('.active_signature:first');
                var selected = sign.attr("user");
                // console.log(selected, 333);
                if(!selected)
                {
                    obj_this.selectedUser = undefined;
                    $('.ng-select-user-list .ng-input input').focus();
                    return;
                }
                let user_index = 0;
                let offSet = 0;
                if (selected)
                {
                    let user_name = sign.find('.user_name').text();
                    obj_this.selectedUser = {id: parseInt(selected), name: user_name}
                    user_index = obj_this.users_list.findIndex(x => x.id ===parseInt(selected));
                    var num = obj_this.users_list.length;
                    var totalHeight = $('.ng-select-user-list .scroll-host')[0].scrollHeight;
                    offSet = user_index * totalHeight/num;
                    $('.scroll-host').animate({
                        scrollTop: offSet
                    }, 100);
                    $('.ng-select-user-list .ng-input input').focus();
                }
            });
            //Pick and drag a new field to page


            function handleDropEvent(event, ui) {
                // console.log(3333);
                var new_signature = $(ui.helper).clone().removeClass('drag').addClass("new_sign");
                new_signature.draggable({
                    containment: "#page_container",
                    scroll: true,
                    cursor: 'move'
                });

                if (parseFloat(new_signature[0].style.top) - $('#page_container').parent().position().top < 0) {
                    return;
                }
                var field_left = parseFloat(new_signature[0].style.left);
                var field_top = parseFloat(new_signature[0].style.top);

                // console.log(field_left, field_top);

                field_top -= ($('.PdfTopBtnsWrapper').height() + 20);
                field_top += $('#viewer_container').scrollTop();

                field_left -= ($('.PdfButtonWrapper').width() + 80);
                field_left += $('#viewer_container').scrollLeft();

                // console.log(field_left, field_top);

                new_signature.css({
                    position: 'absolute',
                    left: field_left,
                    top: field_top,
                });


                if (new_signature.hasClass("text_psition")) {
                    new_signature.html('<input style="display:inline;width:90%" type="text" placeholder="Field Name"/>');
                }

                new_signature.prepend('<i class="fa fa-times  fa-lg del_sign doc-time-del" aria-hidden="true"/>');

                new_signature.attr({
                    "page": pageNum
                }).resizable();


                var after_resized;
                new_signature[0].onresize = function(){
                    var el_this = this;
                    clearTimeout(after_resized);
                    after_resized = setTimeout(function(){
                        on_dropped(el_this);
                    }, 100);
                }
                var field_type = new_signature.find('.field_type');
                let field_name = field_type.html().trim();
                if(field_name == 'Signature' || field_name == 'Initials')
                {
                    new_signature.css({ height:95});
                }

                $('.active_signature').removeClass('active_signature');
                new_signature.addClass('active_signature');
                $('#page_container').append(new_signature);
                if(field_type.html().trim() == 'Text')
                {
                    field_type.replaceWith('<input class="field_type" />');
                    var field_type_input = new_signature.find('.field_type');
                    field_type_input.focus();
                    field_type_input.blur(function(){
                        on_field_type_given(field_type_input);
                    });
                    field_type_input.keyup(function(e){
                        if(e.keyCode == 13)
                        {
                            on_field_type_given(field_type_input);
                        }
                    });
                }
                else{
                    $('#select_user_modal').modal('show');
                }
                on_dropped(new_signature[0], 'creating');
            }

            window['app_libs'].jquery_ui.load(function(){
                //End Dragable
                $('.drag').draggable({
                    helper: "clone",
                    scroll: true,
                    cursor: 'move'
                });
                $("#page_container").droppable({
                    drop: function(evn, ui){
                        // console.log(ui.helper);
                        if($(ui.helper).hasClass('drag'))
                        {
                            handleDropEvent(evn, ui);
                        }
                        else{
                            on_dropped($(ui.helper));
                        }
                    },
                    accept: ".drag,.new_sign",
                    tolerance: "touch",
                });
            });
            
            $(document).off("click", ".save_doc_data")
            $(document).on("click", ".save_doc_data", function(e) {
                var new_divs = $('.new_sign');
                if (!new_divs.length && !obj_this.selected_respondents.length) {
                    return;
                }
                var body = $('<div/>');
                var input_email = $('<h3>Send by Email:</h3><input id="email" placeholder="Email" style="width:50%"/>');
                var input_name = $('<input id="email" placeholder="Name" class="modal-input-wrap" />');
                var input_subject = $('<input id="subject" placeholder="Subject" class="modal-input-wrap rounded" />');
                var email_body = $('<textarea class="o_sign_message_textarea o_input modal-input-wrap rounded"  "rows="4"></textarea>');
                input_subject.val("Signature Request");

                var meeting_id = $('#dropdown_meeting').val();
                body.append("<h6 class='text-primary'>Message</h6>").append(email_body);

                var snd_to_all = $("#check_box_send_all").is(':checked');
                var assign_popup = {
                    on_load: function(){
                        $('#appModal .modal-body').html(body);
                        $('#appModal .modal-header').find('.title').html("<h5>Sign and Return</h5>");
                    },
                    on_save: function(){
                        assign_signatures();
                    },
                    hide_on_save:1
                };
                window['init_popup'](assign_popup);

                function assign_signatures() {
                    var sign_fields = [];
                    // console.log(3232);
                    var isEmpty = false;
                    var subject = input_subject[0].value;
                    var message = email_body[0].value;
                    var email = input_email[1].value;
                    var name = input_name[0].value;

                    if (!snd_to_all) {
                        $.each(new_divs, function() {
                            var sign = $(this);

                            var pg = sign.attr("page");
                            var user = sign.attr("user");
                            if (user == 0 || !user) {
                                isEmpty = true;
                                return;
                            }
                            var field_name = "";
                            var field_type = sign.attr('signtype');
                            field_name = field_type.charAt(0).toUpperCase() + field_type.slice(1);
                            var db_position = sign.attr('position');
                            if(db_position)
                            {
                                db_position = JSON.parse(db_position);
                                var obj = {
                                    document_id: obj_this.doc_id,
                                    token: token,
                                    user_id: user,
                                    field_name: field_name,
                                    email: email,
                                    name: name,
                                    page: pg,
                                    left: db_position.left,
                                    top: db_position.top,
                                    height: db_position.height,
                                    width: db_position.width,
                                    zoom: canvas.width,
                                    type: field_type
                                };
                                sign_fields.push(obj);
                            }
                            else{
                                console.log('No position ', db_position);
                            }
                        });
                        if (isEmpty) {
                            alert("Select user for all fields!!!");
                            return;
                        }
                    }
                    let url = '';
                    if (sign_fields.length != 0 || snd_to_all) {
                        ajax_options = {
                            data: {
                                args: {
                                    app: "esign",
                                    model: "SignatureDoc",
                                    method: "ws_assign_signature",
                                },
                                params: {
                                    document_id: obj_this.doc_id,
                                    token: token,
                                    data: JSON.stringify(sign_fields),
                                    url: url,
                                    meeting_id: meeting_id,
                                    subject: subject,
                                    message: message,
                                    send_to_all: snd_to_all
                                }
                            },
                            onSuccess: function(data) {
                                // obj_this.router.navigate(['/signdocs']);
                                if(data == 'done')
                                {
                                    window.open('/#/signdocs', '_self');
                                }
                                else{
                                    console.log(data, 1343);
                                }
                            }
                        }
                        window['dn_rpc_object'](ajax_options);
                    }
                }
            });

            $(document).off("click", ".sign_container")
            $(document).on("click", ".sign_container", function() {
                var sign_container = $(this);
                var is_my_signature = sign_container.attr("my_record");

                var signature_id = sign_container.attr("id");
                var signature_dom = sign_container;

                function remove_sign(){
                    ajax_options = {
                        data: {
                            args: {
                                app: "esign",
                                model: "Signature",
                                method:"del_sign"
                            },
                            params: {
                                signature_id: signature_id,
                            }
                        },
                        onSuccess: function(data) {
                            sign_container.remove();
                        }
                    }
                    $('#appModal').modal('hide');
                    window['dn_rpc_object'](ajax_options);
                }

                if(obj_this.isAdmin && !obj_this.signature_started)
                {
                    let popup_config = {
                        title: 'Remove Signature',
                        on_load: function(){
                            var modal_body = $('#appModal .modal-body');
                            if(is_my_signature)
                            {
                                var disable_instruction = $('<span>If you want to sign, please disable admin mode.</span>');
                                var disable_admin_btn = $('<button class="btn btn-primary btn-sm">Disable Admin</button>');
                                disable_admin_btn.click(function(){
                                    $('#appModal').modal('hide');
                                    obj_this.socketService.set_admin_mode(false);
                                });
                                modal_body.html(disable_instruction).append(disable_admin_btn);
                            }
                            $('#appModal .modal-footer').find('button:last').before(`
                                <button class="remove btn btn-danger">Remove</button>
                            `);
                            $('#appModal button.remove').click(remove_sign);
                        },
                        no_save:1,
                        hide_on_save: true,
                        on_shown: function(){
                            $('#appModal button.remove').click(remove_sign);
                        }
                    }
                    window['init_popup'](popup_config);
                    return;
                }

                else{
                    if(is_my_signature)
                    {
                        get_signature_data();
                    }
                }

                function get_signature_data()
                {
                    ajax_options = {
                        data: {
                            args: {
                                app: "esign",
                                model: "Signature",
                                method:"load_signature"
                            },
                            params: {
                                signature_id: signature_id,
                                document_id: obj_this.doc_id,
                                token: token,
                                sign_type: sign_container.attr('signtype')
                            }
                        },
                        onSuccess: function(data) {
                            on_sign_got(data);
                        }
                    }
                    if(token){
                        ajax_options.url = '/rest/public';
                    }
                    // console.log(ajax_options.data.params);
                    window['dn_rpc_object'](ajax_options);
                }


                function on_sign_got(sign_data)
                {
                    if(sign_container.attr('signtype') == 'initials' || sign_container.attr('signtype') == 'signature')
                    {
                        let sign_config = {
                            signature_data: sign_data.image,
                            on_signed: function(new_sign){
                                submit_response(new_sign, sign_data.text);
                            },
                            on_auto_sign: function(){
                                get_auto_sign();
                            }
                        };
                        window['app_libs']['signature'].load(()=>{
                            window['init_sign'](sign_config);
                        });
                    }
                    else
                    {
                        let popup_config = {
                            on_load: function(){
                                var selected_sign_type = sign_container.attr('signtype');
                                var read_only = selected_sign_type == 'date' ? 'disabled' : '';
                                selected_sign_type = window['js_utils'].camel_case(selected_sign_type);
                                $('#appModal .modal-header .title:first').html(selected_sign_type);
                                $('#appModal .modal-body').html(`
                                    <input id="sign_data" class="form-control" placeholder="Please Enter `+selected_sign_type+`" value="`+sign_data.text+`" `+read_only+` />
                                `);
                            },
                            on_save:function(){
                                var sign_text = $('#appModal #sign_data').val();
                                submit_response(sign_data.image, sign_text);
                            },
                            hide_on_save: true,
                        }
                        window['init_popup'](popup_config);
                    }

                    function get_auto_sign()
                    {
                        ajax_options = {
                            data: {
                                args: {
                                    app: "esign",
                                    model: "Signature",
                                    method:"get_auto_sign"
                                },
                                params: {
                                    sign_type: sign_container.attr('signtype'),
                                    token: token,
                                }
                            },
                            onSuccess: function(data) {
                                let sign_config = {
                                    signature_data: data.image,
                                    on_signed: function(new_sign){
                                        submit_response(new_sign, sign_data.text);
                                    }
                                };
                                window['app_libs']['signature'].load(()=>{
                                    window['init_sign'](sign_config);
                                });
                            }
                        }
                        if(token){
                            ajax_options.url = '/rest/public';
                        }
                        window['dn_rpc_object'](ajax_options);
                    }
                }

                function submit_response(response_data, sign_data_text)
                {
                    // console.log(response_data, sign_data_text);
                    ajax_options = {
                        data: {
                            args: {
                                app: "esign",
                                model: "Signature",
                                method:"save_signature"
                            },
                            params: {
                                signature_id: signature_id,
                                document_id: obj_this.doc_id,
                                token: token,
                                text: sign_data_text,
                                sign_type: sign_container.attr('signtype'),
                                binary_signature: response_data,
                            }
                        },
                        type:"POST",
                        onSuccess: function(data) {
                            if (data == 'done')
                            {
                                obj_this.router.navigate(['/thanks/Response submitted successfully']);
                            }
                            else{
                                obj_this.signature_started = true;                            
                                for(var i =0;i < doc_data.length; i++)
                                {
                                    // console.log(signature_dom.attr('id'), doc_data[i].id);
                                    if(doc_data[i].id == signature_dom.attr('id'))
                                    {
                                        signature_dom.attr('signed',true);
                                        doc_data[i].image = 'data:image/png;base64,' + data.image;
                                        doc_data[i].signed = true;
                                        on_sign_saved(signature_dom, data);
                                        break;
                                    }
                                }                            
                            }
                        },
                        onError:function(er){
                            window['bootbox'].alert(er);
                            console.log(er);
                        }
                    }
                    if(token){
                        ajax_options.url = '/rest/public';
                    }
                    ajax_options.data.params.type = sign_container.attr('signtype');
                    window['dn_rpc_object'](ajax_options);
                }
            });

            $(document).off("click", ".new_sign .del_sign")
            $(document).on("click", ".new_sign .del_sign", function(e) {
                var sign = $($(this)[0].parentElement);
                sign.fadeOut();
                sign.removeClass("new_sign");
            });


            $(document).off("mousedown", ".new_sign")
            $(document).on("mousedown", ".new_sign", function(e) {
                var sign = $(this);
                $('.active_signature').removeClass('active_signature');
                sign.addClass('active_signature');
            });

            $(document).off("click", ".new_sign")
            $(document).on("click", ".new_sign", function(e) {
                if($(e.target).hasClass('del_sign') || $(e.target).is('input'))
                {
                    return;
                }
                $('#select_user_modal').modal('show');
            });

            var last_focused_sign_number = -1;
            $('#btn_sign_guide').click(function() {
                var my_pending_signs = $.grep(doc_data, function(v) {
                    return !v.signed && v.my_record;
                });
                var clicked_on_save = $(this).attr('on_sign_saved');
                if(clicked_on_save)
                {
                    $(this).removeAttr('on_sign_saved');
                }
                if (my_pending_signs.length == 0) {
                    $(this).hide();
                    if(!clicked_on_save)
                    {
                        window['bootbox'].alert('You have completed assigned signatures, thank you.');
                    }
                    return;
                }
                $(this).html('Next Signature');
                if(last_focused_sign_number == my_pending_signs.length - 1)
                {
                    // var t_message = 'Yoy have seen all '+my_pending_signs.length+' pending signatures';
                    // t_message += ', so welcome back to the first place to sign at document';
                    // window['bootbox'].alert(t_message);
                    last_focused_sign_number = 0;
                }
                else{
                    if(last_focused_sign_number > my_pending_signs.length - 1)
                    {
                        console.log('Index '+last_focused_sign_number+' not valid');
                        last_focused_sign_number = 0;
                    }
                    else{
                        last_focused_sign_number++;
                    }
                }

                var sign = my_pending_signs[last_focused_sign_number];
                var on_page_rendered = function(){
                    var sign_box = $(`.sign_container[id=${sign.id}]:visible:first`);
                    var scroll_el = $('#viewer_container');
                    window['js_utils'].scroll_to_element(sign_box, scroll_el);
                    sign_box.css({
                        border: "solid 3px yellow"
                    })
                }
                renderPage(sign.page, on_page_rendered);
            });


            $('#select_user_modal').on('hidden.bs.modal', function () {
                obj_this.selectedUser = undefined;
                $('.ng-select-user-list .ng-input input').focus();
            });
        });

        function toggle_guide_btn(bool, source=undefined)
        {
            // console.log(bool, source);
            if(bool)
            {
                $('#btn_sign_guide').show();
            }
            else{
                $('#btn_sign_guide').hide();
            }
        }
        toggle_guide_btn(false, 'init');

        function save_attachemnt_to_meeting(){
            ajax_options = {
                data: {
                    args: {
                        app: "esign",
                        model: "SignatureDoc",
                        method: "set_meeting_attachment",
                    },
                    params: {
                        document_id: obj_this.doc_id,
                        meeting_id: $('#dropdown_meeting').val(),
                        send_to_all: $("#check_box_send_all").is(':checked')
                    }
                },
                onSuccess:function(data){
                    if(data != 'done')
                    {
                        obj_this.users_list = data;
                    }
                }
            };
            if(token){
                ajax_options.url = '/rest/public';
            }
            window['dn_rpc_object'](ajax_options);
        }

        function loadData() {
            console.log('Loading doc data', Date());
            window['functions'].showLoader('esign-doc');
            var doc_data_ws = 'ws_get_detail';
            ajax_options = {
                data: {
                    args:{
                        app: 'esign',
                        model: 'SignatureDoc',
                        method: doc_data_ws
                    },
                    params: {
                        document_id: obj_this.doc_id,
                        token: token,
                    }
                },
                onSuccess: function(data) {
                    page_zoom = $('#scaleSelect').val();
                    if(obj_this.is_public && data == 'done')
                    {
                        $('#holder').hide();
                        $('body').prepend('<h1>You have Completed You Signatures</h1>');
                    }
                    if(obj_this.doc_id == 'new')
                    {
                        obj_this.doc_id = data.doc_id;
                        obj_this.doc = {
                            name: data.doc_name,
                            id: data.doc_id
                        }
                    }
                    doc_data = data.doc_data;
                    obj_this.signature_required = data.signature_required;
                    obj_this.signature_started = data.signature_started;
                    if(data.signature_required)
                    {                        
                        toggle_guide_btn(true, 'pending');
                    }
                    obj_this.doc.sign_count = doc_data.length;
                    obj_this.doc.doc_name = data.doc_name || 'Unnamed';

                    var file_path = window['site_config'].server_base_url + data.file_url;
                    console.log('Dcownloading doc from '+file_path, Date());
                    pdf_url = 'data:application/pdf;base64,' + data.binary;
                    if(token)
                    {
                        window['app_libs'].pdf.load(function(){
                            renderPDF(pdf_url);
                        });
                    }
                    else{
                        obj_this.selected_respondents = data.users;
                        obj_this.all_profile_users = data.all_profile_users;
                        obj_this.all_users_list = obj_this.users_list = users = data.users;
                        meeting_id = data.meeting_id;
                        send_to_all = data.send_to_all;                        
                        window['app_libs'].pdf.load(function(){
                            renderPDF(pdf_url);
                        });
                        
                        if(!data.meetings){
                            return;
                        }
                        obj_this.meetings = data.meetings;
                        for(var k=0; k< data.meetings.length; k++)
                        {
                            if(data.meetings[k].id == meeting_id)
                            {
                                obj_this.selectedMeeting = data.meetings[k];
                            }
                        }
                        var ddm = $('#dropdown_meeting');
                        var selected = '';
                        if(!meeting_id)
                        {
                            selected = ' selected';
                        }
                        ddm.html('<option'+selected+' value="">Select Meeting</option>');
                        var option_html = '';
                        data.meetings.forEach(element => {
                            if(meeting_id == element.id)
                            {
                                selected = ' selected';
                            }
                            else
                            {
                                selected = '';
                            }
                            option_html = '<option'+selected+' value='+element.id+'>'+element.name+'</option>';
                            ddm.append(option_html);
                        });
                        if (send_to_all) {
                            $('#check_box_send_all').prop('checked', true);
                            $('.dragabl-fields').hide();
                        }
                        else
                        {
                            $('#check_box_send_all').prop('checked', false);
                            $('.dragabl-fields').show();
                        }
                    }
                },
                onError: function(err){
                    if (token)
                    {
                        window['functions'].hideLoader('esign-doc');
                        window.open(window['site_config'].server_base_url+'/#/feedback/' + err, '_self');
                    }
                    else
                    {
                        console.log(err);
                    }
                    // console.log(err);
                    // $(document).ready(()=>{
                    //     $('#holder').html(`
                    //     <div class="jumbotron vertical-center">
                    //         <div class="container">
                    //             <div class="row text-center">
                    //                 <h3>${err}</h3>
                    //             </div>
                    //             <div class="row text-center">
                    //                 <a class="btn btn-primary" href="${window['site_config'].server_base_url}">Login</a>
                    //             </div>
                    //         </div>
                    //     </div>
                    //     `).show();
                    //     window['functions'].hideLoader('esign-doc');
                    // });
                }
            };
            if(token){
                ajax_options.url = '/rest/public';
            }
            window['dn_rpc_object'](ajax_options);
        }
        loadData();        
        
        function on_sign_saved(signature_dom, data){
            var sign_img = signature_dom.find('img:first');
            var sign_img_src = 'data:image/png;base64,' + data.image;
            signature_dom.attr('signed','true').css('background','white');
            if(sign_img.length > 0)
            {
                sign_img[0].src = sign_img_src;
            }
            else{
                if(signature_dom && signature_dom.length > 0)
                {
                    signature_dom.html('<img src="'+sign_img_src+'" style="width:calc(100% - 10px)" />');
                }
                else{
                    console.log('Invalid signature dom');
                }
            }
            $("#btn_sign_guide").attr('on_sign_saved', 1).click();
        }

        function renderPDF(pdf_url) {
            pdfDoc = null;
            var doc_page_url = window.location.toString().replace(window.location.hostname, '');
            scale = localStorage.getItem(doc_page_url);
            if(scale)
            {
                page_zoom = scale = parseFloat(scale);
            }
            else{
                scale = page_zoom = 1;
            }
            $('#scaleSelect').val(page_zoom);
            canvas = document.getElementById('the-canvas')
            ctx = canvas.getContext('2d');
            try{
                window["PDFJS"].getDocument(pdf_url).then(function getPdf(_pdfDoc) {
                    console.log('Got doc to render', Date());
                    pdfDoc = _pdfDoc;
                    if (!pageNum) {
                        pageNum = 1;
                    }
                    renderPage(pageNum);
                    $('#holder').show();
                    $('.docWrapperContainer').show();
                }).catch(function(er){
                    $('#holder').html('<h3>Sorry document has been removed now</h3>');
                    console.log(er);
                });
            }
            catch(er){
                $('#holder').html('<h3>Sorry document has been removed now</h3>');
                console.log(er);
            }
        }


        function base64ToUint8Array(base64) { //base64 is an encoded byte Array sent from server-side
            var raw = atob(base64); //This is a native function that decodes a base64-encoded string.
            var uint8Array = new Uint8Array(new ArrayBuffer(raw.length));
            for (var i = 0; i < raw.length; i++) {
                uint8Array[i] = raw.charCodeAt(i);
            }
            return uint8Array;
        }

        function renderPage(num, on_page_renderd = undefined) {
            pdfDoc.getPage(num).then(function(page) {
                var viewport = page.getViewport(scale);
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                var renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                page.render(renderContext).then(function(){
                    pageNum = num;
                    document.getElementById('page_num').textContent = pageNum;
                    document.getElementById('page_count').textContent = pdfDoc.numPages;
                    $('.sign_container').hide();
                    $('.new_sign').hide();
                    var selector = '.new_sign[page=' + pageNum + ']';
                    $(selector).show();
                    setTimeout(function() {
                        loadSignatures({
                            "doc_data": doc_data,
                        });
                        if(on_page_renderd)
                        {
                            on_page_renderd();
                        }
                    }, 50);
                    window['functions'].hideLoader('esign-doc');
                }).catch(function (reason) {
                    console.log('stopped ' + reason);
                });
            });
        }

        function on_field_type_given(el){
            var val = el.val();
            // console.log(el[0], val);
            if(val)
            {
                // console.log(val,123);
                el.next().before('<span class="field_type"> : '+val+'</span>');
                el.closest('.active_signature').attr('signtype', val);
                el.remove();
            }
        }

        function on_dropped(el, creating=null){
            // console.log(2343,234234);
            var position = $(el).position();
            let height = $(el).height();
            position = {
                top: parseFloat(position.top),
                left: parseFloat(position.left),
                width: $(el).width() + 25,
                height: height,
            };

            // let field_type = $(el).find('span')[0].innerHTML.toLowerCase();
            // if (field_type == 'signature' || field_type == 'initials')
            // {
            //     height = 95;
            //     position.height = height;
            // }

            var the_canvas = $('#the-canvas');

            if(position.left < 0)
            {
                position.left = 0;
                $(el).css('left', '5px');
            }
            var the_canvas = $('#the-canvas');
            var pos_right = position.left + position.width;
            var pos_bottom = position.top + position.height;

            var canvas_left = the_canvas.position().left;
            var canvas_top = the_canvas.position().top
            var canvas_right = the_canvas.width() + canvas_left;
            var canvas_bottom = the_canvas.height() + canvas_top;

            if(pos_right + 5 > canvas_right)
            {
                position.left = canvas_right - position.width - 5;
                $(el).css('left', position.left+'px');
            }
            if(position.left < 5)
            {
                position.left = 5;
                $(el).css('left', position.left+'px');
            }

            if(pos_bottom + 5 > canvas_bottom)
            {
                position.top = canvas_bottom - position.height - 5;
                $(el).css('top', position.top+'px');
            }
            if(position.top < 5)
            {
                position.top = 5;
                $(el).css('top', position.top+'px');
            }

            var db_pos = {
                top: position.top / page_zoom,
                left: position.left / page_zoom,
                width: position.width / page_zoom,
                height: position.height / page_zoom,
            };
            if(db_pos.left < 10)
            {
                db_pos.left = 10;
            }
            // console.log(position, page_zoom, db_pos, $(el));
            // console.log($(el)[0].innerHTML);
            var db_pos_str = JSON.stringify(db_pos);
            $(el).attr('position',db_pos_str);
        }

        function set_position_on_page(el, position=null){
            try{
                if(!position)
                {
                    position = $(el).attr('position');
                    position = JSON.parse(position);
                }
                if(position.left != 0 && !position.left)
                {
                    console.log('Invalid position', position);
                    return;
                }
                position = {
                    top: position.top,
                    left: position.left,
                    width: position.width,
                    height: position.height,
                };
                var rect = {
                    top: position.top * page_zoom,
                    left: position.left * page_zoom,
                    width: position.width * page_zoom,
                    height: position.height * page_zoom,
                    position: 'absolute',
                }
                if($('#this-canvas').width() < $('#page_container').width())
                {
                    rect.left += $('#the-canvas').position().left;
                }
                // console.log(position, page_zoom, rect);
                $(el).attr('position', JSON.stringify(position));
                $(el).css(rect);
            }
            catch(er){
                console.log('Position attribute not correct', el);
            }
        }

        function zoom_changed(newScale) {
            // Using promise to fetch the page
            page_zoom = newScale;
            var doc_page_url = window.location.toString().replace(window.location.hostname, '');
            localStorage.setItem(doc_page_url, newScale);
            window['functions'].showLoader('zoomin');

            pdfDoc.getPage(pageNum).then(function(page) {
                var viewport = page.getViewport(newScale);
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                // Render PDF page into canvas context
                var renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                page.render(renderContext).then(function(){
                    var saved_new_signs = $('.sign_container:visible,.new_sign');
                    $.each(saved_new_signs, function() {
                        set_position_on_page(this);
                    });
                    window['functions'].hideLoader('zoomin');                    
                });
            });
        }

        function loadSignatures(data) {
            var signature_fields = data.doc_data;
            $.each(signature_fields, function() {
                var field = this;
                var div = $('<div></div>', {
                    id: field.id,
                    signed: field.signed,
                    name: field.name,
                    my_record: field.my_record,
                    page: field.page,
                    field_name: field.field_name,
                    class: "sign_container", 
                    title: window['dt_functions']. getStandardDateTime(field.created_at)
                });
                // console.log(field);
                var show_text = field.type.charAt(0).toUpperCase() + field.type.slice(1);
                div.html(show_text + ":" + field.name);
                div.attr('signtype', field.type);

                set_position_on_page(div, field);

                if (!field.signed && field.my_record) {
                    div.css({
                        background: "rgba(230, 81, 81, 0.9)"
                    });
                }
                if (obj_this.isAdmin)
                {
                    if(field.signed)
                    {
                        if (field.image.indexOf('data:image') > -1)
                        {
                            div.html('<img src="'+field.image+'" style="height:calc(100% - 10px)"/>');
                        }
                        else
                        {
                            div.html('<img src="'+window['site_config'].server_base_url+field.image+'" style="height:calc(100% - 10px)"/>');
                        }
                    }
                }
                else
                {
                    if(field.signed && field.my_record)
                    {
                        if (field.image.indexOf('data:image') > -1)
                        {
                            div.html('<img src="'+field.image+'" style="height:calc(100% - 10px)"/>');
                        }
                        else
                        {
                            div.html('<img src="'+window['site_config'].server_base_url+field.image+'" style="height:calc(100% - 10px)"/>');
                        }
                    }
                }

                if (field.page == pageNum) {
                    $('#page_container').append(div);
                }
            });
        }

        if(obj_this.socketService.admin_mode)
        {
            obj_this.isAdmin = true;
            if (!obj_this.signature_started)
            {
                $('.doc-container').removeClass('user').addClass('admin');
            }
        }
        else{
            $('.doc-container').removeClass('admin').addClass('user');
        }
        obj_this.socketService.call_backs_on_mode_changed['esign'] = function(){
            if(obj_this.socketService.admin_mode)
            {
                obj_this.isAdmin = true;
                if (!obj_this.signature_started)
                {
                    $('.doc-container').removeClass('user').addClass('admin');
                }
            }
            else{
                $('.doc-container').removeClass('admin').addClass('user');
                obj_this.isAdmin = false;
            }
        }
    }
    prev_height = '';
    ngOnDestroy(){
        $('.router-outlet').css('height', this.prev_height);
    }
    
}
