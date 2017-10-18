/* global jQuery */
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';

var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


class EditProfile extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    };
  }

  componentWillMount() {
    const self = this;
    fetch('/api/me', {credentials: 'same-origin'})
      .then(response => {
        if (response.status === 401) {
          return new Promise(null);
        }
        return response.json();
      })
      .then((data) => {
        self.setState({user: data});
      });
  }

  onSave(e) {
    e.preventDefault();

    const csrftoken = getCookie('csrftoken');
    fetch('/api/me', {
      credentials: 'same-origin',
      method: 'PUT',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-type': 'application/json'
      },
      body: JSON.stringify(this.state.user)})
    .then((response) => {
      console.log('saved?');
    });
  }

  onChange(e) {
    const user = this.state.user;
    user[e.target.id] = e.target.value;
    this.setState({user: user});
  }

  render() {
    if (this.state.user === null) {
      return (
        <div className="row">
          <div className="col s6">
            Loading your settings
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        <form className="col s12">
          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="display_name" type="text" className="validate" value={this.state.user.display_name} onChange={this.onChange.bind(this)} />
              <label for="display_name">Derby name</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="email" type="email" className="validate" value={this.state.user.email} onChange={this.onChange.bind(this)} />
              <label for="email">Preferred email address</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="league_affiliation" type="text" className="validate" value={this.state.user.league_affiliation} onChange={this.onChange.bind(this)} />
              <label for="league_affiliation">League affiliation</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="game_history" type="text" className="validate" value={this.state.user.game_history} onChange={this.onChange.bind(this)} />
              <label for="game_history">Game history</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="phone_number" type="text" className="validate" value={this.state.user.phone_number} onChange={this.onChange.bind(this)} />
              <label for="phone_number">Phone number</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="emergency_contact_name" type="text" className="validate" value={this.state.user.emergency_contact_name} onChange={this.onChange.bind(this)} />
              <label for="emergency_contact_name">Emergency contact name</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <input placeholder="" id="emergency_contact_number" type="text" className="validate" value={this.state.user.emergency_contact_number} onChange={this.onChange.bind(this)} />
              <label for="emergency_contact_number">Emergency contact phone number</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s6">
              <a className="center waves-effect waves-light btn" onClick={this.onSave.bind(this)}>Save</a>
            </div>
          </div>

        </form>
      </div>
    );
  }
}

export { EditProfile };
