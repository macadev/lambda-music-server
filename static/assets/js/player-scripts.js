function registerRemoveSongListeners() {
    $('#removeSong').on('click', function (e) {
        node = $(this);
        song_id = node.attr('data-songid');

        var data = {
            'song_id': song_id
        };

        $.ajax({
            url: '/remove-song',
            type: 'POST',
            dataType: 'json',
            contentType: "application/json",
            success: function (data) {
                console.log('Removed song successfully');
                console.log(data);
                node.closest('div').parent().remove();
            },
            headers: {'Content-Type': 'application/json'},
            processData: false,
            data: JSON.stringify(data)
        });
    });
}

$('#submitSong').on('click', function (e) {
    var song_url = $('#song_to_submit').val();

    var data = {
        'song_url': song_url
    };

    $.ajax({
        url: '/submit',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        success: function (data) {
            console.log('Added song successfully!');
            console.log(data);
        },
        headers: {'Content-Type': 'application/json'},
        processData: false,
        data: JSON.stringify(data)
    });
});

var prevNumberOfSongs = 0;

(function playlist_refresher() {
    $.get('/refresh-playlist', function (data) {
        // Now that we've completed the request schedule the next one.
        dataJson = JSON.parse(data);
        var numSongs = dataJson.songs.length;
        if (numSongs > prevNumberOfSongs) {
            refreshedPlaylist = '';
            for (var i = 0; i < numSongs; i++) {

                refreshedPlaylist += "<div class='col-lg-12' id='song'>" +
                                    "<div class='row'>" +
                                        "<div class='col-lg-4'>" +
                                            "<h4><a href=" + dataJson.songs[i].url + ">" + dataJson.songs[i].title + "</a></h4>" +
                                        "</div>" +
                                        "<div class='col-lg-4'>" +
                                            "<h4>" + dataJson.songs[i].duration + "</h4>" +
                                        "</div>" +
                                        "<div class='col-lg-4'>" +
                                            "<p>" + "<a id='removeSong' class='btn btn-md btn-warning'role='button' data-songid=" + dataJson.songs[i].id + ">Remove Song</a></p>" +
                                        "</div>" +
                                    "</div>" +
                                "</div>";
            }
            var $songs = $(refreshedPlaylist);
            $('#playlist').empty().append($songs);
            registerRemoveSongListeners();
        }
        prevNumberOfSongs = numSongs;
        setTimeout(playlist_refresher, 4000);
    });
})();