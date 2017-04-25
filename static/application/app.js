window.App = window.App || {};

App.init = () => {
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
};
App.init();
