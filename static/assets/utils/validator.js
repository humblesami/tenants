//call this function in submit event like following
//if(!isFormValid())
//return;
function isFormValid(form) {
    $('.error').removeClass('error');
    var fields = $(form).find('.pat');
    $(form).find('select').each(function() {
        var ob = $(this);
        if (ob.css('display') == "none" || ob.css('visibility') == "hidden")
            return;
        var index = this.selectedIndex;
        if (index == -1) {
            if (!ob.is('.error'))
                ob.addClass('error');
        } else {
            ob.removeClass('error');
        }
    });
    fields.each(function() {
        validateSingleField($(this));
    });
    if ($('.error').length > 0)
        return false;
    else {
        $('.error').first().focus();
        return true;
    }
}

function validateSingleField(ob) {
    var pat = ob.attr('regex');
    if (!pat)
        return;
    var val = ob.val();
    var re = new RegExp(pat);
    var res = re.test(val);
    if (!res) {
        if (!ob.is('.error'))
            ob.addClass('error');
    } else {
        ob.removeClass('error');
    }
}

$(document).on('keyup', '.pat', function() {
    validateSingleField($(this));
});
$(document).on('blur', '.pat', function() {
    validateSingleField($(this));
});