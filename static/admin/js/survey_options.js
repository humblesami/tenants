(function(){
    function selectionEvent() {        
        $('#questions-group .field-type:not(.taaged) select:visible').each(
            function(i, el) {                
                addChoicesButton(el)
            }
        ).change(function() {
            addChoicesButton(this);
        })
    }
    $('body').on('change', '.field-type:not(.taaged) select:visible', selectionEvent);
    selectionEvent();

    function apply_tagging(el){
        var parent_wrapper = $(el).closest('.form-row');        
        $('.submit-row').find('input[type="submit"]').attr('disabled', 'disabled');        
        var choices_tag_input = parent_wrapper.find('textarea.tags');
        if(!choices_tag_input.length)
        {
            choices_tag_input = parent_wrapper.find('.field-choices textarea').addClass('tags');
        }
        var current_parent = parent_wrapper.find('.field-type')
        current_parent.append(choices_tag_input);
        current_parent.addClass('tagged');
        
        choices_tag_input.tagsInput({
            placeholder: 'Type your choice and press enter to add it.',
            onAddTag: function(){
                choices_tag_input.val($(this).val());
                let choices = $(this).val();
                choices = choices_to_list(choices);
                if (choices.length < 2)
                {
                    current_parent.find('.choice_error').remove();
                    current_parent.append('<span class="choice_error" style="color:red">Please add more than 1 choices</span>');
                    $('.submit-row').find('input[type="submit"]').attr('disabled', 'disabled');
                }
                else
                {
                    current_parent.find('.choice_error').remove();
                    $('.submit-row').find('input[type="submit"]').removeAttr('disabled');
                }
            },
            onRemoveTag: function(){
                choices_tag_input.val($(this).val());
                let choices = $(this).val();
                choices = choices_to_list(choices);
                if( choices.length < 2)
                {
                    current_parent.find('.choice_error').remove();
                    current_parent.append('<span class="choice_error" style="color:red">Please add more than 1 choices</span>');
                    $('.submit-row').find('input[type="submit"]').attr('disabled', 'disabled');
                }
            }
        });
        parent_wrapper.find('.tagsinput').show();
    }    
    
    function choices_to_list(choices) {
        if (choices) {
            return choices.split(',');
        } else {
            return [];
        }
    }
    
    // console.log('abc', 2134);
    function addChoicesButton(el) {
        $('#questions-group table tr td:nth-child(4)').hide();
        $('#questions-group table tr th:nth-child(4)').hide();
        var parent_wrapper = $(el).closest('.form-row');
        parent_wrapper.find('button').remove();        
        if (el.value == 'radio' || el.value == 'select-multiple') 
        {   
            apply_tagging(el);
    
        } else {
            parent_wrapper.find('.tagsinput').hide();
            parent_wrapper.find('.choice_error').remove();
            $('.submit-row').find('input[type="submit"]').removeAttr('disabled');
        }
        parent_wrapper.find('.add-row').click(function() {
            selectionEvent();
        });
    }
})()
