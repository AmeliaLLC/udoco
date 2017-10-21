/* global jQuery*/
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';


const BASE_URL = 'https://www.udoco.org';

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
    console.log('Old: ', this.state.value, 'New: ', e.target.value);
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
      preferences: ['']
    }
  }

  componentWillMount() {
    const url = `${BASE_URL}/api/events/${this.props.match.params.eventId}`;
    fetch(url, {credentials: 'include'})
      .then((response) => (response.json()))
      .then((data) => {
        this.setState({event: data});
      });
  }

  componentDidMount() {
    jQuery('select').material_select();
  }

  onApply(e) {
    e.preventDefault();
    const preferences = this.state.preferences.filter((item) => (item !== ''));
    console.log(preferences);
  }

  onChange(old_value, new_value) {
    /* There's a funny thing here: we always need to preserve the last item as
     * the empty object. This hack where we filter it out and then push it again
     * is how we do that. I'm so sorry. I didn't want to. Blame react, maybe?
     */
    console.log(old_value, new_value);
    let preferences = this.state.preferences.filter((item) => (item !== ''));
    if (old_value === '') {
      preferences.push(new_value);
    } else {
      preferences = preferences.filter((item) => (item !== old_value));
      if (new_value !== '') {
        preferences.push(new_value);
      }
    }
    preferences.push('');
    this.setState({preferences: preferences});
  }

  render() {
    return (
      <div className="row">
        <form className="col s6">
          {(this.state.event !== null &&
          <h5>{this.state.event.title}</h5>
          )}
          <div className="row">
            <div className="input-field col">
              Please select your staffing preferences, starting with your top
              choice, continuing on to your last choice. You may choose as many
              positions as preferences as you would like.
            </div>
          </div>
          {this.state.preferences.map((item, idx) => (
            <Preference change={this.onChange.bind(this)} value={item}/>
          ))}
          <div className="row">
            <div className="input-field col">
              <a onClick={this.onApply.bind(this)} className="center waves-effect waves-light btn">apply</a>
            </div>
          </div>
        </form>
      </div>
    );
  }
}
export default Apply;
