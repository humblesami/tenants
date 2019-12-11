import { Component, OnInit } from '@angular/core';

declare var $:any;

@Component({
  selector: 'app-rtc',
  templateUrl: './rtc.component.html',
  styleUrls: ['./rtc.component.css']
})
export class RtcComponent implements OnInit {

  constructor() { }

  ngOnInit() {
    $('#rtc-container').append('<script src="static/assets/rtc/conference.js"></script>');
  }

}
