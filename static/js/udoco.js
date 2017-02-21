var App = {
    Models: {},
    Collections: {},
    Views: {}
};

App.Models.Event = Backbone.Model.extend({
    urlRoot: '/api/events'
});

App.Collections.Events = Backbone.Collection.extend({
    Model: App.Models.Event,
    url: '/api/events',
    parse: function(response) {
        return response.results;
    }
});

App.Router = Backbone.Router.extend({
    routes: {
        '': 'index',
        'events/:id': 'viewEvent'
    },

    index: function() {
        new App.Views.Calendar();
    },
    viewEvent: function(id) {
        new App.Views.EventApply({eventId: id});
    }
});
