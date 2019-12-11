import { Component, OnInit, Input, Output } from '@angular/core';
import { HttpService } from '../../app/http.service';
import { NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
declare var $:any;
@Component({
  selector: 'app-movetomyfolder',
  templateUrl: './movetomyfolder.component.html',
  styleUrls: ['./movetomyfolder.component.css']
})
export class MovetomyfolderComponent implements OnInit {
  httpService: HttpService;
  @Input() doc_id : number;
  folder_id = '';
  records = undefined;
  constructor(private httpServ: HttpService,
    private activeModal: NgbActiveModal
    ) { 
    let obj_this = this;
    obj_this.httpService = httpServ;
  }

  move_to_my_folder(folder, doc)    
    {
        // doc.moved = true;
        var file_id = doc;
        let obj_this = this;
        var folder_id = obj_this.folder_id
        let input_data = {
            args:{
                app:'chat',
                model:'message',
                method:'move_to_other_folder',
            },
            no_loader:1,
            params: {
                 file_id: file_id,
                 folder_id: folder_id
            },
        }
        obj_this.httpService.post(input_data, (data:any)=>{                      
            // console.log(data,22233333333233333333);
            obj_this.close_modal(data);
        } , function(){
            console.log("Nothing");
        });    
    }
    close_modal(data){
        // console.log(data,12222212121);
        this.activeModal.close(data);
    }

  folders_recursive_childs(){
    let obj_this = this;
    let args = {
        app: 'resources',
        model: 'Folder',
        method: 'get_my_folder_recursive'
    }
    let final_input_data = {
        params: {
            
        },
        args: args
    };
    // console.log(final_input_data.params, 333);
    obj_this.httpService.get(final_input_data,
    (result: any) => {
        console.log(result);
        // obj_this.on_result(result);
        obj_this.records = result;

        function asaan(){
          var root_folder = obj_this.records;
  
          function set_parent_paths(afolder){
              for (var key in afolder.sub_folders){
                  var parent_path = [];
                  if(afolder.parent_path)
                  {
                      parent_path = afolder.parent_path.slice(0);
                  }
                  parent_path.push(afolder.id);
                  afolder.sub_folders[key].parent_path = parent_path;
                  set_parent_paths(afolder.sub_folders[key]);                
              }
          }
  
          function get_parent(obj){
              var parent_obj = root_folder;
              if(!obj.parent_path)
              {
                  return parent_obj;
              }
              var i = 0;
              for(var id of obj.parent_path)
              {
                  i++;
                  if(i == 1){
                      continue;
                  }
                  parent_obj = parent_obj.sub_folders[id];
              }
              return parent_obj;
          }
  
          var opened_folder = undefined
          function show_parent(){
              // console.log(opened_folder, 133);
              if(opened_folder){
                  var obj = get_parent(opened_folder);
                  show_folder(obj);
              }
          }
  
          function show_folder(obj){
              opened_folder = obj;
              var par = '';
              par += '<input type="hidden" value="'+obj.id+'">';
              par += '<button class="btn btn-primary btn_paste">Paste</button>';
              $('#name').html(obj.name);
              $('#action').html(par);

              var lis = '';
              for(var child_id in obj.sub_folders){
                  lis += '<li class="p-1 border-bottom">';
                    lis += '<div class="row">';
                        lis += '<div class="col-3 offset-1">'
                            lis += '<i class="icon-folder" ></i> '+obj.sub_folders[child_id].name;
                        lis += '</div>'
                        lis += '<input type="hidden" value="'+child_id+'">';
                        lis += '<div class="ml-auto">'
                            lis += '<div class="d-flex">';
                            // console.log(4544);
                                if(Object.keys(obj.sub_folders[child_id].sub_folders).length)
                                {
                                    lis += '<button  class="btn btn-info btn_open_folder">Open</button>';
                                }
                                lis += '<button class="btn btn-primary btn_paste">Paste</button>'
                            lis += '</div>';
                        lis += '</div>';
                    lis += '</div>';
                  lis += '</li>';
              }
              console.log()
              $('#ul_sub_folders').html(lis);
              var cnt = 0;
              $('#parent_div').children().each(function(){
                $(this).find('.btn_paste').click(function(){
                  var ch_id = $(this).closest('span').find('input').val();
                  obj_this.folder_id = ch_id;
                  obj_this.move_to_my_folder(ch_id,obj_this.doc_id);
              });

              });
              $('#ul_sub_folders').children().each(function(i, el){
                  $(this).find('.btn_open_folder').click(function(){
                      var ch_id = $(this).closest('li').find('input').val();
                      var active_sub_folder = obj.sub_folders[ch_id];
                    //   console.log(active_sub_folder,obj.id, ch_id);
                      show_folder(active_sub_folder);
                  });

                  $(this).find('.btn_paste').click(function(){
                    var ch_id = $(this).closest('li').find('input').val();
                    obj_this.folder_id = ch_id;
                    obj_this.move_to_my_folder(ch_id,obj_this.doc_id);
                });
              })
          }
  
          $('#btn_open_parent').click(show_parent);
          set_parent_paths(root_folder);
          console.log(root_folder);
          show_folder(root_folder);
      }
        asaan();
    },null);  
  }

  ngOnInit() {

      let obj_this = this
      obj_this.folders_recursive_childs();
           
    


  }

}
