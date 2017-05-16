$(document).ready(function(){
    var onetouchLoader = $('.js-onetouchLoader');
    if(onetouchLoader.length){
        checkStatus();
    }
    $('.message .close').on('click', function() {
        $(this).closest('.message').transition('fade')
        ;
    });
});

function checkStatus(){
    $.get('/authy-check/', function(data){
        if(data == 'pending'){
            setTimeout(function(){
                checkStatus();
            }, 1000);
        }
        else if(data == 'approved'){
            window.location.href = "/";
        }
        else if(data == 'denied'){
            alert('OneTouch Request Was denied. Redirecting to Login Page.')
            window.location.href = "/login";
        }
    });
}