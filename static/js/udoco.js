componentHandler.reset = function() {
    var components = document.querySelectorAll('[data-upgraded]'); 
    if (components.length > 0) {
        componentHandler.downgradeElements(components);
    }
    componentHandler.upgradeAllRegistered();
}

var App = {
    Models: {},
    Collections: {},
    Views: {},

    init: function() {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        Backbone._sync = Backbone.sync;
        Backbone.sync = function(method, model, options){
            options.beforeSend = function(xhr){
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            };
            return Backbone._sync(method, model, options);
        };

        $.get('/api/me').done(function(response) {
            if (response !== '') {
                App.state.user = new App.Models.Official(response);
                if (response.league) {
                    App.state.user.league = new App.Models.League(response.league);
                }
            }
            App.state.router = new App.Router();
            Backbone.history.start();
        });
    },
    toast: function(message) {
        var container = $('#toast')[0];
        container.MaterialSnackbar.showSnackbar(message);
    },
    state: {
        navigation: null,
        router: null,
        user: null
    }
};

App.Models.Official = Backbone.Model.extend({
    urlRoot: '/api/officials'
});
App.Models.League = Backbone.Model.extend({
    urlRoot: '/api/leagues'
});
App.Models.Event = Backbone.Model.extend({
    urlRoot: '/api/events'
});
App.Models.Application = Backbone.Model.extend({
    urlRoot: function() {
        return '/api/events/'+this.event+'/applications';
    }
});
App.Models.Roster = Backbone.Model.extend({
    urlRoot: function() {
        return '/api/events/'+this.event+'/rosters';
    }
});
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

App.Views.Navigation = Backbone.View.extend({
    el: "#navigation",
    events: {
        'click #settings': '_settingsClick',
        'click .material-icons': '_navClick'
    },
    stack: [{title: 'United Derby Officials Colorado'}],
    template: _.template($('#navigation-template').html()),
    initialize: function(options) {
        this.drawer = new App.Views.NavigationDrawer();
        this.render();
    },
    render: function() {
        this.$el.html(this.template(this));
        this.drawer.render();
    },
    push: function(data) {
        this.stack.push(data);
        this.render();
    },
    pop: function() {
        if (this.stack.length > 1) {
            this.stack.pop();
            this.render();
        }
    },

    _settingsClick: function(e) {
        e.preventDefault();
        App.state.router.navigate('/profile', {trigger: true});
    },
    _navClick: function(e) {
        if (this.stack.length > 1) {
            /* XXX: rockstar (28 Feb 2017) - This should work
             * as a back button, but I've got too much shit to
             * worry about right now to sort that out.
             */
        }
    }
});
App.Views.NavigationDrawer = Backbone.View.extend({
    el: "#drawer",
    events: {
        'click #settings_drawer': '_settingsClick',
    },
    template: _.template($('#drawer-template').html()),
    render: function() {
        this.$el.html(this.template(this));
    },

    _settingsClick: function(e) {
        this.$el.removeClass('is-visible');
        $('.mdl-layout__obfuscator').removeClass('is-visible');
        e.preventDefault();
        App.state.router.navigate('/profile', {trigger: true});
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
        this.undelegateEvents();
        this.$el.html('');
        App.state.router.navigate('/', {trigger: true});
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
            var selects = this.$el.find('.mdl-selectfield__select');
            console.log(selects.length);
            if (selects.length > 13) { return; }
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
            App.toast({'message': 'Your application has been received.'});
            this._close();
        }, this));
    },
    onCancel: function() {
        this._close();
    },
    onWithdraw: function() {
        $.post('/_/events/'+this.event.id+'/withdraw', _.bind(function() {
            App.toast({'message': 'Your application has been withdrawn.'});
            this._close();
        }, this));
    }
});

App.Views.EditProfile = Backbone.View.extend({
    el: '#content',
    events: {
        'click #save': '_save',
        'click #cancel': '_cancel'
    },
    model: null,
    template: _.template($('#edit-profile-template').html()),
    initialize: function() {
        this.model = App.state.user;
        this.render();
    },
    render: function() {
        this.$el.html(this.template(this));
    },

    _save: function(e) {
        e.preventDefault();
        this.model.set('display_name', this.$el.find('#id_display_name').val());
        this.model.set('email', this.$el.find('#id_email').val());
        this.model.set('phone_number', this.$el.find('#id_phone_number').val());
        this.model.set('game_history', this.$el.find('#id_game_history').val());
        this.model.set('emergency_contact_name', this.$el.find('#id_emergency_contact_name').val());
        this.model.set('emergency_contact_number', this.$el.find('#id_emergency_contact_number').val());
        this.model.set('league_affiliation', this.$el.find('#id_league_affiliation').val());
        this.model.save().done(function() {
            App.toast({'message': 'Profile saved'});
        });
    },
    _cancel: function(e) {
        e.preventDefault();
        App.state.router.navigate('/', {trigger: true});
    },
});

App.Views.Calendar = Backbone.View.extend({
    el: "#content",
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
        App.state.router.navigate('events/'+event.id, {trigger: true});
    }
});

App.Router = Backbone.Router.extend({
    routes: {
        '': 'index',
        'events/:id': 'viewEvent',
        'profile': 'editProfile',
        '_=_': 'afterLogin'
    },

    onRoute: function(route, params) {
        componentHandler.reset();
    },
    initialize: function(options) {
        App.state.navigation = new App.Views.Navigation();
        this.on('route', _.bind(this.onRoute, this));
    },

    afterLogin: function() {
        this.navigate('/', {trigger: true});
    },
    index: function() {
        App.state.navigation.pop();
        new App.Views.Calendar();
    },
    editProfile: function() {
        App.state.navigation.push({title: 'Edit your profile'});
        new App.Views.EditProfile();
    },
    viewEvent: function(id) {
        App.state.navigation.pop();
        new App.Views.EventApply({eventId: id});
    }
});
