function removeSong(song_id) {

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
            $("input[data-songid='" + song_id + "']").closest("tr").remove();
        },
        headers: { 'Content-Type': 'application/json' },
        processData: false,
        data: JSON.stringify(data)
    });

}