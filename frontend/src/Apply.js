/* global jQuery */
/* global Materialize */
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';
import { getCSRFToken } from './utils.js';
import { BaseURL } from './config.js';

const PreferenceOptions = [
  {value: '', label: 'Choose your option'},
  {value: '0', label: 'Head ref'},
  {value: '1', label: 'Inside pack ref'},
  {value: '2', label: 'Jam ref'},
  {value: '3', label: 'Outside pack ref'},

  {value: '5', label: 'Head NSO'},
  {value: '6', label: 'Penalty tracker'},
  {value: '7', label: 'Penalty wrangler'},
  {value: '8', label: 'Inside whiteboard'},
  {value: '9', label: 'Jam time'},
  {value: '10', label: 'Scorekeeper'},
  {value: '11', label: 'Scoreboard operator'},
  {value: '12', label: 'Penalty box manager'},
  {value: '13', label: 'Penalty box timer'},
  {value: '14', label: 'Lineup tracker'}
];


/* Feature request: only show the items that haven't already been chosen. */
class Preference extends Component {
  constructor(props) {
    super(props);
    this.state = {
      value: this.props.value
    }
  }

  static propTypes = {
    change: PropTypes.func.isRequired
  }

  onChange(e) {
    //console.debug('Old: ', this.state.value, 'New: ', e.target.value);
    this.props.change(this.state.value, e.target.value);
    this.setState({value: e.target.value});
  }

  render() {
    return (
      <div className="row">
        <div className="input-field col s12 m12 l6 xl6">
          <select className="browser-default" name="preference[]" onChange={this.onChange.bind(this)} value={this.state.value}>
            {PreferenceOptions.map((item) => (
            <option value={item.value} selected={(this.state.value === item.value) ? '1' : '0'}>{item.label}</option>
            ))}
          </select>
        </div>
      </div>
    );
  }
}

class Apply extends Component {
  constructor(props) {
    super(props);
    this.state = {
      event: null,
      name: '',
      email: '',
      user: null,
      preferences: ['']
    }
  }

  componentWillMount() {
    const url = `${BaseURL}/api/events/${this.props.match.params.eventId}`;
    fetch(url, {credentials: 'include'})
      .then((response) => (response.json()))
      .then((data) => {
        if (data.detail === undefined) {
          this.setState({event: data});
        }
      })
      .catch(() => {});

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
      });
  }

  componentDidMount() {
    jQuery('select').material_select();
  }

  onApply(e) {
    e.preventDefault();

    let url = `${BaseURL}/api/events/${this.props.match.params.eventId}/applications/`;
    let body = this.state.preferences.filter((item) => (item !== ''));
    console.log(this.state.user);
    if (this.state.user === null) {  // Loser application
      url = `${BaseURL}/api/events/${this.props.match.params.eventId}/lapplications/`;
      body = {
        name: this.state.name,
        email: this.state.email,
        preferences: this.state.preferences.filter((item) => (item !== ''))
      };
    }
    fetch(url, {
      credentials: 'include',
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      },
      body: JSON.stringify(body)})
      .then((response) => {
        if (response.status === 409) {
          Materialize.toast('You cannot apply to this event at this time.', 10000);
        } else if (response.status === 201) {
          Materialize.toast('Your application has been received.', 10000)
        }
      })
      .catch((err) => {
        console.log(err);
        Materialize.toast('An unknown error has occurred.', 10000)
      });
  }

  onChange(old_value, new_value) {
    /* There's a funny thing here: we always need to preserve the last item as
     * the empty object. This hack where we filter it out and then push it again
     * is how we do that. I'm so sorry. I didn't want to. Blame react, maybe?
     */
    /* There is a bug here when preferences are deselected. I think it's also
     * a react issue, but IDGAF.
     */
    let preferences = this.state.preferences.filter((item) => (item !== ''));
    if (old_value === '') {  // New value
      preferences.push(new_value);
    } else if (new_value !== '') {  // Swapped value
      preferences[preferences.indexOf(old_value)] = new_value;
    } else {  // Removed value
      preferences = preferences.filter((item) => (item !== old_value));
    }
    preferences.push('');
    this.setState({preferences: preferences});
  }

  onNameChange(e) {
    e.preventDefault();
    this.setState({name: e.target.value});
  }

  onEmailChange(e) {
    e.preventDefault();
    this.setState({email: e.target.value});
  }

  render() {
    return (
      <div className="row">
        {(this.state.event !== null &&
        <form className="col s6">
          <h5>{this.state.event.title}</h5>
          <div className="row">
            <div className="input-field col">
              Please select your staffing preferences, starting with your top
              choice, continuing on to your last choice. You may choose as many
              positions as preferences as you would like.
            </div>
          </div>
          {(this.state.user === null &&
            <div className="row">
              <div className="input-field col s6">
                <input placeholder="" id="name" type="text" className="validate" value={this.state.name} onChange={this.onNameChange.bind(this)} />
                <label for="name">Derby name</label>
              </div>
            </div>
          )}
          {(this.state.user === null &&
            <div className="row">
              <div className="input-field col s6">
                <input placeholder="" id="email" type="email" className="validate" value={this.state.email} onChange={this.onEmailChange.bind(this)} />
                <label for="email">Email address</label>
              </div>
            </div>
          )}
          {this.state.preferences.map((item, idx) => (
            <Preference change={this.onChange.bind(this)} value={item}/>
          ))}
          <div className="row">
            <div className="input-field col">
              <a onClick={this.onApply.bind(this)} className="center waves-effect waves-light btn">apply</a>
            </div>
          </div>
        </form>
        )}
        {(this.state.event === null &&
        <div className="col s6">
          Event not found. Please <a href="/_">return to the events listing</a>
        </div>
        )}
      </div>
    );
  }
}
export default Apply;
