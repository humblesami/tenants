import { Component, OnInit,Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
    selector: 'app-userlistmodal',
    templateUrl: './userlistmodal.component.html',
    styleUrls: ['./userlistmodal.component.css']
})
export class UserlistmodalComponent implements OnInit {
    @Input() user_input_str = '';
    @Input() selection_input_str = '';
    @Input() add_only = 0;
    constructor(public activeModal: NgbActiveModal) {
        
    }
    selected_users = [];
    on_user_selected(selected_users=[]) {
        // console.log(selected_users);
        this.selected_users = selected_users;
    }

    sendRecord(){
        this.activeModal.close(this.selected_users);
    }

    ngOnInit() {
        
    }
}