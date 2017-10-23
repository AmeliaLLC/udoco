/* global jQuery */
/* global Materialize */
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';
import moment from 'moment';
import { Link } from 'react-router-dom';
import { BaseURL } from './config.js';
import { getCSRFToken } from './utils.js';


class EventGroup extends Component {
  static propTypes = {
    label: PropTypes.string.isRequired,
    events: PropTypes.array.isRequired
  }

  render() {
    return (
      <ul className="collapsible">
        <li className="blue-grey lighten-4">{this.props.label}</li>
        {this.props.events.map((item) => {
          return (<Event event={item} />);
        })}
      </ul>
    );
  }
}

class Event extends Component {
  static propTypes = {
    event: PropTypes.object.isRequired
  }

  onWithdraw(e) {
    e.preventDefault();

    const url = `${BaseURL}/api/events/${this.props.event.id}/applications`;
    fetch(url, {
      credentials: 'include',
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then((response) => {
      if (response.status === 204) {
        Materialize.toast('You have withdrawn from this event.', 10000);
      } else {
        Materialize.toast('An error has occurred. Unable to withdraw.', 10000);
      }
    })
  }

  render() {
    const event = this.props.event;
    return (
      <li>
        <div className="collapsible-header">
          {event.league} presents - {event.title}
        </div>
        <div className="collapsible-body">
          <div className="row">
            <div className="col s4">
              <b>Location</b>
            </div>
            <div className="col s8">
              {event.location}
            </div>
          </div>
          <div className="row">
            <div className="col s4">
              <b>Call time</b>
            </div>
            <div className="col s8">
              {`${moment(event.start.replace('Z', '')).subtract(1, 'hours').format('hh:mm a')}`}
            </div>
          </div>
          {(event.has_applied &&
          <div className="row">
            <div className="col s12">
              <a href="" onClick={this.onWithdraw.bind(this)} className="center waves-effect waves-light btn">withdraw application</a>
            </div>
          </div>
          )}
          {(event.can_apply &&
          <div className="row">
            <div className="col s12">
              <Link to={`/_apply/${event.id}`} className="center waves-effect waves-light btn">apply</Link>
            </div>
          </div>
          )}
          {(!event.is_authenticated &&
          <div className="row">
            <div className="col s12">
              <a href="/auth/login/facebook" className="center waves-effect waves-light btn" >log in to apply</a>
              <div className="row">
                We use Facebook for logins so you don't have to remember another
                username/password. <a href={`/_apply/${event.id}/luser`}>I'd rather not use Facebook</a>
              </div>
            </div>
          </div>
          )}
        </div>
      </li>
    );
  }
}


class EventList extends Component {
  static propTypes = {
    league: PropTypes.bool,
    schedule: PropTypes.bool
  }

  static defaultProps = {
    league: false,
    schedule: false
  }

  constructor(props) {
    super(props);
    this.state = {
      groups: [],
      grouped_events: {},
      events: []
    };
  }

  componentWillMount() {
    const self = this;
    const FORMAT = 'D MMM YYYY';
    let url = `${BaseURL}/api/events`;
    if (this.props.schedule) {
      url = `${BaseURL}/api/schedule`;
    } else if (this.props.league) {
      url = `${BaseURL}/api/league_schedule`;
    }
    fetch(url, {credentials: 'include'})
      .then((response) => (response.json()))
      .then((data) => {
        // XXX: rockstar (22 Oct 2017) - I'm not sure what this is about.
        // Sometimes it's data.results, sometimes just results.
        if (data.results !== undefined) {
          data = data.results;
        }
        const results = data.filter((item) => {
          return moment().diff(moment(item.start.replace('Z', ''))) < 0;
        });
        const new_events = [];
        const groups = [];

        results.map((item) => {
            let date = moment(item.start.replace('Z', ''));

            let key = date.format(FORMAT);
            if (new_events[key] === undefined) {
              groups.push(key);
              new_events[key] = [item];
            } else {
              new_events[key].push(item);
            }
            return false;
        });

        groups.sort((a, b) => {
          const first = moment(a, FORMAT);
          const second = moment(b, FORMAT);
          return first.isBefore(second) ? -1 : 1;
        });

        self.setState({
          events: results,
          groups: groups,
          grouped_events: new_events
        });
      })
      .catch((err) => console.warn('Failure fetching events: ', err));
  }

  componentDidUpdate() {
    jQuery('.collapsible').collapsible();
    jQuery('.tooltipped').tooltip({delay: 50});
  }

  render() {
    return (
      <section>
        {this.state.groups.map((item) => {
        return (
          <EventGroup label={item} events={this.state.grouped_events[item]} />
        )
        })}
      </section>
    );
  }
}

export { EventList };
