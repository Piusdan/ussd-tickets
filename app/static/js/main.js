// Data Picker Initialization
$('#date').bootstrapMaterialDatePicker({ weekStart : 0, time: false, format : 'DD/MM/YY', minDate : moment() });

$(function() { //shorthand document.ready function
    $('#create_eventForm').on('submit', function(e) { //use on if jQuery 1.7+
        e.preventDefault();  //prevent form from submitting
        var data = $("#create_eventForm :input").serializeArray();
        var json_data = [];
        console.log(data)
        console.log(JSON.stringify(data)); //use the console for debugging, F12 in Chrome, not alerts
        document.getElementById('create_eventForm').reset();
        $('#createEventModal').modal('toggle');
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        showNotification(colorName, 'Event Form submitted', placementFrom, placementAlign, animateEnter, animateExit);
        var url = '/event/create'
        $.ajax({
            url: url,
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (data, textStatus, jQxhr) {
                var text = data.data
                showNotification(colorName, text, placementFrom, placementAlign, animateEnter, animateExit);
            },
            processData: false,
            error: function (jqXhr, textStatus, errorThrown) {
                // var colorName = "bg-red"
                showNotification("bg-red", errorThrown, placementFrom, placementAlign, animateEnter, animateExit);
            }
        });

    });
});

$(function () {
    $('.add-ticket-button button').on('click', function () {
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var form = document.getElementById("add_ticket")
        var price = form.getElementsByClassName('price')[0].value
        var count = form.getElementsByClassName('count')[0].value
        // form.hide();
//         dom_doc = new DOMParser().parseFromString(form, "text/html");
        var url = '/ticket/update'
        // event.preventDefault();
        $.ajax({
            url: url,
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify({
                "ticket_id": ticket_id,
                "price": price,
                "count": count
            }),
            success: function (data, textStatus, jQxhr) {
                var text = data.data
                // alert(text)
                showNotification(colorName, text, placementFrom, placementAlign, animateEnter, animateExit);
            },
            processData: false,
            error: function (jqXhr, textStatus, errorThrown) {
                // var colorName = "bg-red"
                showNotification(colorName, errorThrown, placementFrom, placementAlign, animateEnter, animateExit);
            }
        });

    });
});

function showNotification(colorName, text, placementFrom, placementAlign, animateEnter, animateExit) {
    if (colorName === null || colorName === '') { colorName = 'bg-black'; }
    if (text === null || text === '') { text = 'Turning standard Bootstrap alerts'; }
    if (animateEnter === null || animateEnter === '') {
//        an
        imateEnter = 'animated fadeInDown';
    }
    if (animateExit === null || animateExit === '') { animateExit = 'animated fadeOutUp'; }
    var allowDismiss = true;

    $.notify({
        message: text
    },
        {
            type: colorName,
            allow_dismiss: allowDismiss,
            newest_on_top: true,
            timer: 500,
            placement: {
                from: placementFrom,
                align: placementAlign
            },
            animate: {
                enter: animateEnter,
                exit: animateExit
            },
            template: '<div data-notify="container" class="bootstrap-notify-container alert alert-dismissible {0} ' + (allowDismiss ? "p-r-35" : "") + '" role="alert">' +
            '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
            '<span data-notify="icon"></span> ' +
            '<span data-notify="title">{1}</span> ' +
            '<span data-notify="message">{2}</span>' +
            '<div class="progress" data-notify="progressbar">' +
            '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>' +
            '</div>' +
            '<a href="{3}" target="{4}" data-notify="url"></a>' +
            '</div>'
        });
}