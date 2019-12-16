$(function () {
	function addFileInputs()
	{
		var fileinputs = $(".attachment").not('.fileinput');
		fileinputs.fileinput();
		fileinputs.addClass('fileinput');
	}
    setTimeout(() => {
        // console.log($('.inline_doc_set .add-row a').length, 3434);
        $('.inline_doc_set .add-row a').click(function(){
            // console.log(4444);
            setTimeout(addFileInputs, 500);
        });
    }, 500);
    
});
