$('#removeSong').on('click', function(e) {
    node = $(this);
    song_id = node.attr('data-songid');

    var data = {
        'song_id' : song_id
    };

    $.ajax({
        url: '/remove-song',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            console.log('Removed song successfully');
            console.log(data);
            node.closest('div').parent().remove();
        },
        headers: { 'Content-Type': 'application/json' },
        processData: false,
        data: JSON.stringify(data)
    });
});

$('#submitSong').on('click', function(e) {
    var song_url = $('#song_to_submit').val();

    var data ={
        'song_url': song_url
    };

    $.ajax({
        url: '/submit',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            console.log('Added song successfully!');
            console.log(data);
        },
        headers: { 'Content-Type': 'application/json' },
        processData: false,
        data: JSON.stringify(data)
    });


});