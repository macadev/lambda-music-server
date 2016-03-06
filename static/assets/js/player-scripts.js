var currentPlaylist = [];

function registerRemoveSongListeners() {
    $('.removeSong').each(function() {
        $(this).on('click', function (e) {
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
                    node.closest('div').parent().parent().remove();
                },
                headers: {'Content-Type': 'application/json'},
                processData: false,
                data: JSON.stringify(data)
            });
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

(function playlist_refresher() {
    localPlaylistSongIDs = {};
    var playlistLength = currentPlaylist.length;
    for (var i = 0; i < playlistLength; i++) {
        localPlaylistSongIDs[currentPlaylist[i].id] = 1;
    }

    $.ajax({
            url: '/refresh-playlist',
            type: 'POST',
            dataType: 'json',
            contentType: "application/json",
            headers: {'Content-Type': 'application/json'},
            processData: false,
            data: JSON.stringify(localPlaylistSongIDs),
            success: function (newSongs) {
                var numSongs = newSongs.songs.length;
                if (numSongs > 0) {
                    refreshedPlaylist = '';
                    for (var i = 0; i < numSongs; i++) {
                        currentPlaylist.push(newSongs.songs[i]);
                        refreshedPlaylist +=
                            "<div class='col-lg-12' id='song'>" +
                            "<div class='row'>" +
                            "<div class='col-lg-4'>" +
                            "<h4><a href=" + newSongs.songs[i].url + ">" + newSongs.songs[i].title + "</a></h4>" +
                            "</div>" +
                            "<div class='col-lg-4'>" +
                            "<h4>" + newSongs.songs[i].duration + "</h4>" +
                            "</div>" +
                            "<div class='col-lg-4'>" +
                            "<p>" + "<a class='btn btn-md btn-warning removeSong' role='button' data-songid=" + newSongs.songs[i].id + ">Remove Song</a></p>" +
                            "</div>" +
                            "</div>" +
                            "</div>";
                    }
                    $(refreshedPlaylist).hide().appendTo('#playlist').fadeIn(2000);
                    registerRemoveSongListeners();
                }
                setTimeout(playlist_refresher, 4000);
            }
    });
})();