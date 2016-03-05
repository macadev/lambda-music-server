function removeSong(song_id) {

    var data = {
        'song_id' : song_id
    };

    $.ajax({
        url: '/search-realtime',
        type: 'POST',
        data: data,
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            console.log('Removed song successfully');
        },
        headers: { 'Content-Type': 'application/json' },
        processData: false,
        data: JSON.stringify(data)
    });

}