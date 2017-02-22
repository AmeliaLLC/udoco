var App = {
    Models: {},
    Collections: {},
    Views: {},

    user: null
};

App.Models.Official = Backbone.Model.extend({});

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

App.Views.EventApply = Backbone.View.extend({
    el: "#dialog-target",
    events: {
        'change .mdl-selectfield__select': 'onPreferenceChange',
        'click #event-withdraw': 'onWithdraw',
        'click #event-apply': 'onApply',
        'click #event-cancel': 'onCancel'
    },
    template: _.template($('#event-apply').html()),
    initialize: function(options) {
        this.event = new App.Models.Event({id: options.eventId});
        this.event.fetch().done(_.bind(function(data) {
            this.render();
        }, this));
    },
    render: function() {
        this.$el.html(this.template(this));
        this._addPreferenceChoice();
        this.$el[0].showModal();
    },

    event: null,
    _addPreferenceChoice: function() {
        var select = $('#preference-select').html();
        this.$el.find('form').append(select);

        var ele = this.$el.find('.mdl-js-selectfield').last()[0];
        if (ele) {
            componentHandler.upgradeElement(ele);
        }
    },
    _close: function() {
        var el = this.$el[0];
        if (el.open) {
            el.close();
        }
        this.$el.html('');
        router.navigate('/', {trigger: true});
    },
    onPreferenceChange: function(event) {
        var target = event.target,
            parent = this.$el.find(target.parentNode);
        if (event.target.value === "") {
            if (this.$el.find('select').length > 1) {
                parent.remove()
            }
        } else {
            if (parent.hasClass('is-invalid')) {
                parent.removeClass('is-invalid');
            }

            /* TODO: Make sure that, should the value change, we aren't
             * adding due to a change in an already populated field.
             */
            if (target == this.$el.find('.mdl-selectfield__select').last()[0]) {
                    //&& this.$el.find('.mdl-selectfield').length == 1) {
                this._addPreferenceChoice();
            }

            /* TODO: make sure that the values are all unique */
        }
    },
    onApply: function() {
        var form = this.$el.find('#preference-form'),
            selects = form.serializeArray(),
            items = selects.map(function(ele) {
                    return ele.value;
                }).filter(function(val) {
                    return (val != "");
                });

        /* Make sure at least one choice was picked. */
        if (items.length < 1) {
            var error = this.$el.find('.mdl-selectfield__error');
            error.text('Please select a staffing preference.')
            error.parent().addClass('is-invalid');
        }

        $.post(form[0].action, {'preferences': items}, _.bind(function() {
            /* TODO: Add toast message */
            this._close();
        }, this));
    },
    onCancel: function() {
        this._close();
    },
    onWithdraw: function() {
        $.post('/_/events/'+this.event.id+'/withdraw', _.bind(function() {
            /* TODO: Add toast message */
            this._close();
        }, this));
    }
});

App.Views.Calendar = Backbone.View.extend({
    el: "#js",
    template: _.template($('#app-template').html()),
    initialize: function() {
        this.events = new App.Collections.Events();
        this.events.fetch().done(_.bind(function(data) {
            this.render();
        }, this));
    },
    render: function() {
        this.$el.html(this.template(this));
        this.$el.find('#calendar').fullCalendar({
            editable: false,
            events: this.events.toJSON(),
            displayEventTime: true,
            handleWindowResize: true,
            weekends: true,
            defaultView: 'month',
            columnFormat: 'ddd',
            eventClick: _.bind(this.onEventClick, this),
            header: {
                left: 'prev,next',
                center: 'title',
                right: ''
            }
        });
    },

    events: null,
    onAddEventClick: function(event) {
        window.location = '/events/new';
    },
    onEventClick: function(event) {
        router.navigate('events/'+event.id, {trigger: true});
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
