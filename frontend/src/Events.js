/* global jQuery */
/* global Materialize */
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';
import moment from 'moment';
import { Link } from 'react-router-dom';
import { BaseURL } from './config.js';
import { getCSRFToken } from './utils.js';
import { Navbar } from './Navigation.js';
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';

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
          return (<Event event={item} renderWithdraw={this.props.renderWithdraw} cancelEvent={this.props.cancelEvent}/>);
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

    const url = `${BaseURL}/api/games/${this.props.event.id}/applications/0/`;
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
        Materialize.toast('You have withdrawn from this event.', 1500);
        this.props.renderWithdraw(this.props.event.id);
      } else {
        Materialize.toast('An error has occurred. Unable to withdraw.', 1500);
      }
    })
  }

  render() {
    const event = this.props.event;
    return (
      <li>
        <div className="collapsible-header">
          <div className="row marginLess">
            <div className="col s11 eventHeader">
              {event.league} presents - {event.title}
            </div>
            <div className="col s1">
              <p className="arrowHolder">
                <a href={`/games/${event.id}`} title="direct game link">
                  <i className="right material-icons noRightLeft moveRightALittle" >chevron_right</i>
                </a>
              </p>
            </div>
          </div>
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
              <b>Start time</b>
            </div>
            <div className="col s8">
              {`${moment(event.start).format('hh:mm a')}`}
            </div>
          </div>

          <div className="row">
            <div className="col s4">
              <b>Call time</b>
            </div>
            <div className="col s8">
              {`${moment(event.start).subtract(1, 'hours').format('hh:mm a')}`}
            </div>
          </div>
          {event.complete &&
            <div className="row">
              <div className="col s12">
                <b>This game is no longer accepting applications.</b>
              </div>
            </div>
          }


          {((event.has_applied && !event.complete) &&
          <div className="row">
            <div className="col s12 m6">
              <a href="" onClick={this.onWithdraw.bind(this)} className="center waves-effect waves-light btn blue-grey darken-4 col s12">withdraw application</a>
            </div>
          </div>
          )}

          {(event.can_apply &&
          <div className="row">
            <div className="col s12 m6">
              <Link to={`/apply/${event.id}`} className="center waves-effect waves-light btn blue-grey darken-4 col s12">apply</Link>
            </div>
          </div>
          )}

          {(event.can_schedule &&
            <div className="row">
              <div className="col s12 m6">
                <Link to={`/games/${event.id}/schedule`} className="center waves-effect waves-light btn blue-grey darken-4 col s12">{this.props.event.complete?'view rosters':'schedule event'}</Link>
              </div>
            </div>
          )}

          {((event.can_schedule && !event.complete) &&
            <div className="row">
              <div className="col s12 m6">
                <Link to={`/games/${event.id}/edit`} className="col s12 center waves-effect waves-light btn blue-grey darken-4">Edit Event Information</Link>
              </div>
            </div>
          )}

          {((event.can_schedule) &&
            <div className="row">
              <div className="col s12 m6">
                <button className="col s12 center waves-effect waves-light btn blue-grey darken-4" onClick={()=>{this.props.cancelEvent(event.id)}}>Cancel Event</button>
              </div>
            </div>
          )}


          {((!event.is_authenticated && !event.complete) &&
          <div className="row">
            <div className="col s12">
              <a href="/auth/login/facebook" className=" blue-grey darken-4 center waves-effect waves-light btn " >log in to apply</a>
              <div className="row">
                We use Facebook for logins so you don't have to remember another
                username/password. <a href={`/apply/${event.id}/luser`}>I'd rather not use Facebook</a>
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
  componentWillReceiveProps(nextProps){
    const self = this;
    const FORMAT = 'D MMM YYYY';
    let url = `${BaseURL}/api/games`;
    if (nextProps.schedule) {
      url = `${BaseURL}/api/schedule`;
    } else if (nextProps.league) {
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
          return moment().diff(moment(item.start)) < 0;
        });
        const new_events = [];
        const groups = [];

        results.map((item) => {
            let date = moment(item.start);

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

  componentWillMount() {
    const self = this;
    const FORMAT = 'D MMM YYYY';
    let url = `${BaseURL}/api/games`;
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
          return moment().diff(moment(item.start)) < 0;
        });
        const new_events = [];
        const groups = [];

        results.map((item) => {
            let date = moment(item.start);

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
  renderWithdraw = (id)=>{
    const FORMAT = 'D MMM YYYY';
    let eventsCopy = this.state.events.slice('');
    let groupedEventsCopy = Object.assign({}, this.state.grouped_events);
    let withdrawnEvent = eventsCopy.find((event)=>(event.id===id));
    let date = moment(withdrawnEvent.start).format(FORMAT);
    withdrawnEvent.can_apply = true;
    withdrawnEvent.has_applied = false;
    let groupedEventToUpdate = groupedEventsCopy[date].find((event)=>(event.id===id));
    groupedEventToUpdate.can_apply = true;
    groupedEventToUpdate.has_applied = false;
    this.setState({events: eventsCopy, grouped_events: groupedEventsCopy});

  }
  cancelEvent = (eventId)=>{
    confirmAlert({
      title: 'Cancel Event?',
      message: 'This will notify all applicants. Are you sure?',
      confirmLabel: 'Yes',
      cancelLabel: 'Nevermind',
      onConfirm: ()=>{
        fetch(`${BaseURL}/api/games/${eventId}`,{
          method: 'DELETE',
          credentials: 'include',
          headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-type': 'application/json'
          }
        })
        .then(response=>{
          if(response.status !== 204){
            return;
          }
          let relevantEvent = this.state.events.find(event=>event.id===eventId);
          let eventsCopy = this.state.events.slice('');
          let keptEvents = eventsCopy.filter(event=>event.id !== eventId);
          let groupedEventsCopy = Object.assign({},this.state.grouped_events);
          let key = moment(relevantEvent.start).format('D MMM YYYY')
          groupedEventsCopy[key] = groupedEventsCopy[key].filter(event=>event.id !== eventId);
          if(groupedEventsCopy[key].length === 0){
            let filteredGroupsCopy = this.state.groups.filter(group=>group!==key)
            delete groupedEventsCopy[key];
            this.setState({events: keptEvents, grouped_events: groupedEventsCopy, groups: filteredGroupsCopy},()=>{
              Materialize.toast('This event was cancelled.', 1500);
            });
          }else{
            this.setState({events: keptEvents, grouped_events: groupedEventsCopy},()=>{
              jQuery('.collapsible').trigger('collapse');
              Materialize.toast('This event was cancelled.', 1500);
            });
          }
        })
      }
    });
  }

  render() {
    return (
      <div>
      <Navbar user={this.props.user} button={this.props.league?{
        text: "Add Event",
        to: "/games/new",
        icon: "add_circle_outline"
      }:null}/>
        <section>
          {this.state.groups.map((item) => {
          return (
              <EventGroup label={item} renderWithdraw={this.renderWithdraw} events={this.state.grouped_events[item]} cancelEvent={this.cancelEvent}/>
          )
          })}
        </section>
      </div>
    );
  }
}

export { EventList };
