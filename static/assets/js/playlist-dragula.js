var dragAndDrop = {

    init: function () {
        this.dragula();
        this.eventListeners();
    },

    eventListeners: function () {
        this.dragula.on('drop', this.dropped.bind(this));
    },

    dragula: function () {
        this.dragula = dragula([document.querySelector('#playlist')]);
    },

    dropped: function (el) {
        console.log('dropped!')
    }

};

dragAndDrop.init();