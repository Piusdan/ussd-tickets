// clickabel table rows
$(function() {
      $(".clickableRow").on("click", function() {
          location.href="http://google.com";
      });
});
// Data Picker Initialization
$('#date').bootstrapMaterialDatePicker({ weekStart : 0, time: false, format : 'DD/MM/YYYY', minDate : moment(), nowButton: true, nowText: 'Today' });
$('#startdate').bootstrapMaterialDatePicker({ weekStart : 0, time: false, format : 'DD/MM/YYYY', minDate : moment(), nowButton: true, nowText: 'Today' });
$('#enddate').bootstrapMaterialDatePicker({ weekStart : 0, time: false, format : 'DD/MM/YYYY', minDate : moment() });
$(function() {
//uses ajax to submit request to create event
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

$(function() {
//uses ajax to submit request to create event
    $('#edit_eventForm').on('submit', function(e) { //use on if jQuery 1.7+
        e.preventDefault();  //prevent form from submitting
        var data = $("#edit_eventForm :input").serializeArray();
        var json_data = [];
        console.log(data)
        console.log(JSON.stringify(data)); //use the console for debugging, F12 in Chrome, not alerts
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var event_id = $(this).attr('data-eventId');
        var url = '/event/update/' + event_id
        $('edit-event-preloader').show();
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

$(function() {
//uses ajax to submit request to create event
    $('#add_packageForm').on('submit', function(e) { //use on if jQuery 1.7+
        e.preventDefault();  //prevent form from submitting
        $('#add_packageModal').modal('toggle');
        var data = $("#add_packageForm :input").serializeArray();
        var json_data = [];
        console.log(data)
        console.log(JSON.stringify(data)); //use the console for debugging, F12 in Chrome, not alerts
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var event_id = $(this).attr('data-package-eventId');
        var url = '/package/add/' + event_id
        document.getElementById('add_packageForm').reset();
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
        location.reload(false);

    });
});

$(function() {
//uses ajax to submit request to add a new user
    $('#add_userForm').on('submit', function(e) { //use on if jQuery 1.7+
        e.preventDefault();  //prevent form from submitting
        $('#add_userModal').modal('toggle');
        var data = $("#add_userForm :input").serializeArray();
        var json_data = [];
        console.log(data)
        console.log(JSON.stringify(data)); //use the console for debugging, F12 in Chrome, not alerts
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var event_id = $(this).attr('data-package-eventId');
        var url = '/add-user'
        document.getElementById('add_userForm').reset();
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
        location.reload(false);

    });
});

$(function() {
//uses ajax to submit request to top up a user
    $('#topUpForm').on('submit', function(e) { //use on if jQuery 1.7+
        e.preventDefault();  //prevent form from submitting
        console.log("clicked")
        $('#topUpModal').modal('toggle');
        var data = $("#topUpForm :input").serializeArray();
        var json_data = [];
        console.log(data)
        console.log(JSON.stringify(data)); //use the console for debugging, F12 in Chrome, not alerts
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var user_id = $(this).attr('data-userId');
        var url = '/edit-profile/'+user_id
        document.getElementById('topUpForm').reset();
        $.ajax({
            url: url,
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (data, textStatus, jQxhr) {
                var text = data.payload
                showNotification(colorName, text, placementFrom, placementAlign, animateEnter, animateExit);
            },
            processData: false,
            error: function (jqXhr, textStatus, errorThrown) {
                // var colorName = "bg-red"
                showNotification("bg-red", errorThrown, placementFrom, placementAlign, animateEnter, animateExit);
            }
        });
//        location.reload(false);

    });
});


$(function () {
// edit package ajax
    $('.edit-package-button button').on('click', function (e) {
        e.preventDefault();
        var placementFrom = $(this).data('placement-from');
        var placementAlign = $(this).data('placement-align');
        var animateEnter = $(this).data('animate-enter');
        var animateExit = $(this).data('animate-exit');
        var colorName = $(this).data('color-name');
        var package_id = $(this).attr('data-packageid');
        var form = document.getElementById(package_id)
        var price = form.getElementsByClassName('price')[0].value
        var number = form.getElementsByClassName('number')[0].value
        // form.hide();
//         dom_doc = new DOMParser().parseFromString(form, "text/html");
        var url = '/package/update'
        // event.preventDefault();
        $.ajax({
            url: url,
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify({
                "package_id": package_id,
                "price": price,
                "number": number
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

function writeDate(e) {
    var date = this.innerHTML
    this.innerHTML= moment(date).fromNow();
    console.log(moment(date).fromNow())
}

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