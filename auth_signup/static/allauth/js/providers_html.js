(function(){
    let elForm = document.querySelector('.page-content form');
    let ii = 0;
    while(elForm && ii<10){
        if(elForm.nextElementSibling && elForm.nextElementSibling.innerHTML.trim() == 'Or use a third-party'){
            elForm.nextElementSibling.remove();
            break
        }
        elForm = elForm.nextElementSibling;
        ii += 1;
        console.log(3536456, ii);
    }
})()
