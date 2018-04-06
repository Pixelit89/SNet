$(document).ready(function () {
    $('#send').click(function () {
        // alert($('#message').val());
        $.ajax({
            url: 'http://127.0.0.1:8001',
            type: 'POST',
            data: $('#message').val(),
            success: function(data) {
                // alert(data);
                $('#answer').append("<p>"+data+"</p>")
            }
        });
    })
})