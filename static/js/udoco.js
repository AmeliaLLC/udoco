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

        $.get('/api/me?old=1').done(function(response) {
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
        'click #event-contact': 'onContact',
        'click #event-withdraw': 'onWithdraw',
        'click #event-apply': 'onApply',
        'click #event-cancel': 'onCancel',
        'click #event-schedule': 'onSchedule',
        'click #event-close': 'onClose',

        'click #loserify': 'onLoserify'
    },
    template: _.template($('#event-apply').html()),
    initialize: function(options) {
        this.event = new App.Models.Event({id: options.eventId});
        this.event.on('destroy', _.bind(this._afterEventDestroy, this));
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
    _afterEventDestroy: function() {
        App.toast({'message': 'Your event has been deleted.'});
        this._close();
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
        this.$el.find('.is-invalid').removeClass('is-invalid');
        var target = event.target,
            parent = this.$el.find(target.parentNode);
        if (event.target.value === "") {
            if (this.$el.find('select').length > 1) {
                parent.remove()
            }
        } else {
            /* TODO: Make sure that, should the value change, we aren't
             * adding due to a change in an already populated field.
             */
            var selects = this.$el.find('.mdl-selectfield__select');
            if (selects.length > 13) { return; }
            if (target == this.$el.find('.mdl-selectfield__select').last()[0]) {
                    //&& this.$el.find('.mdl-selectfield').length == 1) {
                this._addPreferenceChoice();
            }
        }
    },
    onApply: function() {
        var form = this.$el.find('#preference-form');
        if (form.length > 0) {
            var selects = form.serializeArray(),
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
                return;
            }

            /* Make sure there are no duplicates */
            var $elements = this.$el.find('select');
            $elements.each(function () {
                    var selectedValue = this.value;

                    var dupes = $elements.not(this)
                        .filter(function() {
                            return this.value == selectedValue;
                        }).parent().addClass('is-invalid');
                });
            this.$el.find('.is-invalid').find('.mdl-selectfield__error').text(
                 'You have chosen this option twice');
            if (this.$el.find('.is-invalid').length > 0) { return };

            $.post(form[0].action, {'preferences': items}, _.bind(function() {
                App.toast({'message': 'Your application has been received.'});
                this._close();
            }, this));
        } else {
            form = this.$el.find('#loser-preference-form');
            var values = form.serializeArray(),
                name = values.filter(function(i) {
                    if (i.name == 'name') { return i }})[0].value,
                email = values.filter(function(i) {
                    if (i.name == 'email') { return i }})[0].value,
                selects = values.filter(function(i) {
                    if (i.name == 'staffing[]') { return i }}),
                items = selects.map(function(ele) {
                        return ele.value;
                    }).filter(function(val) {
                        return (val != "");
                    });

            if (items.length < 1) {
                var error = this.$el.find('.mdl-selectfield__error');
                error.text('Please select a staffing preference.')
                error.parent().addClass('is-invalid');
                return;
            }

            /* Make sure there are no duplicates */
            var $elements = this.$el.find('select');
            $elements.each(function () {
                    var selectedValue = this.value;

                    var dupes = $elements.not(this)
                        .filter(function() {
                            return this.value == selectedValue;
                        }).parent().addClass('is-invalid');
                });
            this.$el.find('.is-invalid').find('.mdl-selectfield__error').text(
                 'You have chosen this option twice');
            if (this.$el.find('.is-invalid').length > 0) { return };

            $.ajax({
                url: '/api/events/'+this.event.get('id')+'/loserapplications/',
                data: JSON.stringify({
                    'derby_name': name, 'email': email, 'preferences': items}),
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                //dataType: 'json',
                success: _.bind(function() {
                    App.toast({'message': 'Your application has been received.'});
                    this._close();
                }, this)
            });
        }
    },
    onContact: function() {
        window.location = '/events/'+this.event.get('id')+'/contact';
    },
    onCancel: function() {
        this.event.destroy()
    },
    onSchedule: function() {
        window.location = '/events/'+this.event.get('id')+'/schedule';
    },
    onClose: function() {
        this._close();
    },
    onWithdraw: function() {
        $.post('/_/events/'+this.event.id+'/withdraw', _.bind(function() {
            App.toast({'message': 'Your application has been withdrawn.'});
            this._close();
        }, this));
    },
    onLoserify: function(e) {
        e.preventDefault();
        this.$el.find('#authenticate').css({'display': 'none'});
        this.$el.find('#loser-apply').css({'display': 'block'});
        this.$el.find('.mdl-dialog__actions').prepend(
            '<button type="button" class="mdl-button" id="event-apply">Apply</button>');
        componentHandler.reset();
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
        '_=_': 'index'
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
        if (this.calendar === undefined) {
            this.calendar = new App.Views.Calendar();
        }
    },
    editProfile: function() {
        App.state.navigation.push({title: 'Edit your profile'});
        this.calendar = undefined;
        new App.Views.EditProfile();
    },
    viewEvent: function(id) {
        App.state.navigation.pop();
        new App.Views.EventApply({eventId: id});
    }
});
