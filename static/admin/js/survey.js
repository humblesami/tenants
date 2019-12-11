function selectionEvent()
  {
    $('#questions-group .field-type select:visible').each(
      function(i, el){
        addChoicesButton(el)
      }
    ).change(function(){
      addChoicesButton(this);
    })
  }

function on_add_choice_click(el){
  let element = this;
  let choices = $(element).parent().next().find('textarea').val();
  config = {
  on_load: function(){
        $('#appModal .modal-body').html('<input type="text" value="'+choices+'" class="tag_input" placeholder="Pres Enter to Add your choices"/>');
        $('.tag_input').tagsInput({
          placeholder: 'Type your choice and press enter to add it.'
        });
    },
    on_close:function(){
      let choices = $('.tag_input').val()
      choices_list = choices_to_list(choices);
      let parent = $(element).parent();
      if (choices_list.length <= 1)
      {
        parent.find('.choice_error').remove();
        parent.append('<span class="choice_error" style="color:red">Please add more than 1 choices</span>');
        $('.submit-row').find('input[type="submit"]').attr('disabled', 'disabled');
      }
      else
      {
        parent.find('.choice_error').remove();
        $('.submit-row').find('input[type="submit"]').removeAttr('disabled');
        $('#appModal').modal('hide');
      }
      append_choices(parent, choices);
    }
  }
  window['init_popup'](config);
}
  selectionEvent();
  function append_choices(el, choices)
  {
    let selection_value = el.find('select')[0].value;
      let choices_list = choices_to_list(choices);
      el.next().find('textarea').val(choices);
      el.find('.choice_list').remove();
      var text_field = $(el).closest('tr').find('td.field-text');
      for (let i in choices_list)
      {
        if (selection_value == 'radio')
        {
            text_field.append('<div class="choice_list"><input name="'+choices_list[i]+'" type="radio" disabled><label for="scales">'+choices_list[i]+'</label></div>');
        }
        else if (selection_value == 'select-multiple')
        {
            text_field.append('<div class="choice_list"><input name="'+choices_list[i]+'" type="checkbox" disabled><label for="scales">'+choices_list[i]+'</label></div>');
        }
      }
  }
  function choices_to_list(choices)
  {
    if (choices)
    {
      return choices.split(',');
    }
    else
    {
      return [];
    }
  }
  // console.log('abc', 2134);
  function addChoicesButton(el){
    $('#questions-group table tr td:nth-child(4)').hide();
    $('#questions-group table tr th:nth-child(4)').hide();
    var parent = $(el).parent();
    parent.find('button').remove();

    if (el.value == 'radio' || el.value == 'select-multiple')
    {
      parent.find('.choice_list').show();
      var add_choices_btn = $('<div><button style="background: rgb(65, 118, 144) !important" class="btn btn-primary add_choices_btn my-3" type="button">Add Choices</button></div>');
      var text_field = $(el).closest('tr').find('td.field-text');
      text_field.append(add_choices_btn);
      add_choices_btn.click(on_add_choice_click);
      append_choices(parent,parent.next().find('textarea').val());
      setTimeout(() => {
        if (!parent.next().find('textarea').val())
        {
          $('.add_choices_btn').click();
        }
      }, 100);
    }
    else
    {
      parent.find('.choice_list').hide();
      parent.find('button').remove();
      parent.find('.choice_error').remove();
      $('.submit-row').find('input[type="submit"]').removeAttr('disabled');
    }
    $('.add-row').click(function(){
      selectionEvent();
    });
  }