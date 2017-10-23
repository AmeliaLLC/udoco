/* global Materialize */
import React, { Component } from 'react';
import {getCSRFToken} from './utils.js';
import { BaseURL } from './config.js';


class EditProfile extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    };
  }

  componentWillMount() {
    const self = this;
    fetch(`${BaseURL}/api/me`, {credentials: 'include'})
      .then(response => {
        if (response.status === 401) {
          return new Promise((resolve, reject) => resolve(null));
        }
        return response.json();
      })
      .then((data) => {
        self.setState({user: data});
      })
      .catch(() => {
        console.warn('Not logged in');
      });
  }

  componentDidUpdate() {
    Materialize.updateTextFields();
  }

  onSave(e) {
    e.preventDefault();

    fetch(`${BaseURL}/api/me`, {
      credentials: 'include',
      method: 'PUT',
      headers: {
        'X-CSRFToken': getCSRFToken(),
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
