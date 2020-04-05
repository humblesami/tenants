$(document).ready(function(){
    durationRequisits();
    $(document).on('blur',
        '.field-duration input, .field-start_date input, .field-end_date input',
        function()
        {
            let time_difference = undefined;
            if (check_durations_with_time())
            {
                $('.field-duration .error').remove();
            }
            if ($(this).closest('p').hasClass('datetime'))
            {
                var dt_val = $(this).val().trim();
                if (!dt_val)
                {
                    $(this).closest('.form-row').find('.error').remove();
                    //console.log($(this).closest('.datetime')[0]);
                    $(this).closest('.datetime').before(`<span class="error text-danger">This field is required.</span>`);
                    $('.submit-row input[type="submit"]').attr('disabled', 'disabled');
                    return;
                }
                else
                {
                    //console.log(dt_val, 513);
                    $(this).closest('.form-row').find('.error').remove();
                    $('.submit-row input[type="submit"]').removeAttr('disabled');
                }
            }
            time_difference = get_time_difference();
            if (time_difference < 0)
            {
                $('.field-end_date .error').remove();
                $('.field-end_date').append(`
                <span class="error text-danger">
                End Date should be greater than Start Date.
                </sapn>`);
                $('.submit-row input[type="submit"]').attr('disabled', 'disabled');
                return;
            }
            else
            {
                $('.field-end_date .error').remove();
                $('.submit-row input[type="submit"]').removeAttr('disabled');
            }



            if ($(this).closest('td').hasClass('field-duration'))
            {
                if ($(this).closest('tr').find('.field-name input').val() && time_difference)
                {
                    duration_in_mil = get_total_durations();
                    console.log(23,234);
                    if (duration_in_mil > time_difference)
                    {
                        $('.submit-row input').attr('disabled', 'disabled');
                        $('.field-duration div.error').remove();
                        $(this).closest('td').append(`<div class="error text-danger">Duration must be less than meeting time.</div>`);
                        $('.submit-row input[type="submit"]').attr('disabled', 'disabled');
                    }
                    else
                    {
                        $('.field-duration div.error').remove();
                        $('.submit-row input[type="submit"]').removeAttr('disabled');
                    }

                }
            }
        });
    $('.djn-add-item a').click(function(){
        setTimeout(durationRequisits,100);
    });
    $(document).on('click', '.datetimeshortcuts a', function(){
        $(this).parent().parent().find('.error').remove();
    });


    function check_durations_with_time()
    {
        let time_difference = get_time_difference();
            let total_durations = get_total_durations();
            if (total_durations > time_difference)
            {
                $('.submit-row .error').remove();
                $('.submit-row').prepend(`
                <span class="error text-danger">Agenda duration must be less than meeting time</span>
                `)
                return false;
            }
            else
            {
                $('.submit-row .error').remove();
                return true;
            }
    }
    $(document).on('click', '.submit-row input[type="submit"]',
        function(e){
            if(!check_durations_with_time())
            {
                e.preventDefault();
            }

    })

    function checkDateAndTime(meetingDate)
    {
        let is_valid = false;
        for (let i=0; i<meetingDate.length;i++)
        {
            if (!meetingDate[i])
            {
                is_valid = false;
                return is_valid;
            }
            else
            {
                is_valid = true;
            }
        }
        return is_valid;
    }

    function durationRequisits()
    {
        $(".field-duration input:visible").each(function(){
            var obj = this;
            var is_pat = $(obj).hasClass('pat');
            // console.log(is_pat, obj)
            if (!is_pat)
            {
                $(obj).addClass('pat');
                $(obj).mask('00:00');
                $(obj).attr('regex', '^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$');
                $(obj).attr('placeholder', 'HH:MM');
            }
        });
    }
    function durationToMilliseconds(duration)
    {
        hours_to_mil = duration[0] * 60 * 60 * 1000;
        minuts_to_mil = duration[1] * 60 * 1000;
        return hours_to_mil + minuts_to_mil;
    }
    function get_time_difference()
    {
        let end_date = [];
        let start_date = [];
        $('.field-start_date input').each(function(el){
            let value = $(this).val();
            if (value)
            {
                start_date.push(value);
            }
        });

        $('.field-end_date input').each(function(el){
            let value = $(this).val();
            if (value)
            {
                end_date.push(value);
            }
        });

        if(start_date.length != 2 && end_date.length !=2)
        {
            return;
        }

        start_date = new Date(Date.parse(start_date.join(' ')));
        end_date = new Date(Date.parse(end_date.join(' ')));
        var diff = moment.duration(moment(end_date).diff(moment(start_date)));
        return diff.valueOf()
    }

    function get_total_durations()
    {
        let total_durations = [0,0]
        $(".field-duration input:visible").each(function(){
            let duration = [];
            duration = $(this).val().split(':')
            for(let i=0; i<duration.length;i++){
                if(!isNaN(parseInt(duration[i])))
                {
                    total_durations[i] += parseInt(duration[i]);
                }
            }
        });
        return durationToMilliseconds(total_durations);
    }
});
