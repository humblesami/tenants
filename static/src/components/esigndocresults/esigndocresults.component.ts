import { Component, OnInit } from '@angular/core';
import {HttpService} from '../../app/http.service';
import {ActivatedRoute} from '@angular/router';
import {Router} from '@angular/router';
import { SocketService } from 'src/app/socket.service';
declare var $: any;

@Component({
  selector: 'app-esigndocresults',
  templateUrl: './esigndocresults.component.html',
  styleUrls: ['./esigndocresults.component.css', '../surveyresults/surveyresults.css']
})
export class EsigndocresultsComponent implements OnInit {

  esignDetails: any;
  socketService: SocketService;
  constructor(private httpService: HttpService,
    private route: ActivatedRoute, private ss: SocketService,
    public router: Router) {
    this.socketService = this.ss;
  }

  ngOnInit() {
    const obj_this = this;
    const input_data = {
        document_id: obj_this.route.snapshot.params.id
    };
    const success_cb = function(result) {
        obj_this.esignDetails = result;

        if (obj_this.esignDetails.progress_data.length)
        {
            obj_this.esignDetails.progress_data[0].color = '#EF6262';
            obj_this.esignDetails.progress_data[1].color = '#7CD122';
        }
        for(let obj of obj_this.esignDetails.progress_data)
        {
            obj.color 
        }

        setTimeout(function() {
            var chart_colors = window['chart_colors'];
            for (let i in obj_this.esignDetails.results) {
                let esign_result = obj_this.esignDetails.results[i];
                if (esign_result.progress_data.length) {
                    var p =0;
                    for(let j in esign_result.progress_data){
                        if(p>=chart_colors.length)
                        {
                            p = 0;
                        }
                        esign_result.progress_data[j].color = chart_colors[p++];
                    }
                    window['app_libs']['chart'].load(()=>{
                        window['drawChart'](esign_result.progress_data, '#chartData-' + esign_result.id);
                    });
                }
            }
            if (obj_this.esignDetails.progress_data) {
                window['app_libs']['chart'].load(()=>{
                window['drawChart'](obj_this.esignDetails.progress_data, '#progress-chart');
                });
            }
        }, 800)
    };
    const failure_cb = function(error) {
        // console.log(error)
        // obj_this.router.navigate(['/survey/' + obj_this.route.snapshot.params.id]);
    };
    let args = {
        app: 'esign',
        model: 'SignatureDoc',
        method: 'get_results'
    }
    let final_input_data = {
        params: input_data,
        args: args
    };
    obj_this.httpService.get(final_input_data, success_cb, failure_cb);
  }

}
