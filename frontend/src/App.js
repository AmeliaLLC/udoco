/* global jQuery*/
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import Apply from './Apply.js';
import './App.css';

class Navbar extends Component {
  componentDidMount() {
    /* TODO: check to see if logged in */
    jQuery('.button-collapse').sideNav();
    jQuery('.collapsible').collapsible();
  }
  render() {
    return (
    <nav className="nav-extended blue-grey darken-4">
      <div className="nav-wrapper">
        <a href="/" className="brand-logo center">UDO CO</a>
        <a href="#!" data-activates="hambarglar" className="button-collapse">
          <i className="material-icons">menu</i>
        </a>

        <ul id="nav-non-mobile" className="left hide-on-med-and-down">
          <li>
              <a href="/profile">
                <i className="left material-icons">perm_identity</i>Profile
              </a>
          </li>
          <li>
              <a href="/schedule">
                <i className="left material-icons">today</i>My Schedule
              </a>
          </li>
          <li>
              <a href="/manage">
                <i className="left material-icons">supervisor_account</i>Manage League
              </a>
          </li>
        </ul>

        <ul id="hambarglar" className="side-nav">
          <li>
              <a href="/profile">
                <i className="material-icons">perm_identity</i>Profile
              </a>
          </li>
          <li>
              <a href="/schedule">
                <i className="material-icons">today</i>My Schedule
              </a>
          </li>
          <li>
              <a href="/manage">
                <i className="material-icons">supervisor_account</i>Manage League
              </a>
          </li>
        </ul>
      </div>
    </nav>
    );
  }
}


class DateSeparator extends Component {
  static propTypes = {
    date: (props, propName, componentName) => {
      const prop = props[propName];
      if (typeof(prop) !== 'object' || prop.getDate === undefined) {
          debugger;
        return new Error(
          'Invalid prop `' + propName + '` supplied to' +
          ' `' + componentName + '`. Validation failed.'
        );
      }
    }
  }
  render() {
    return (
      <li className="blue-grey lighten-4">{`${this.props.date}`}</li>
    );
  }
}

class Event extends Component {
  static propTypes = {
    title: PropTypes.string.isRequired,
    address: PropTypes.string.isRequired,
    eventId: PropTypes.number.isRequired,
    callTime: PropTypes.string.isRequired,
    league: PropTypes.string.isRequired
  }
  render() {
    return (
      <li className="collection-item">
        <div className="collapsible-header">
          {this.props.league} Presents - {this.props.title}
        </div>
        <div className="collapsible-body">
          <div className="row">{this.props.address}</div>
          <div className="row">Call time: {this.props.callTime}</div>
          <div className="row">
            <a href={`/apply/${this.props.eventId}`} className="center waves-effect waves-light btn">apply</a>
          </div>
        </div>
      </li>
    );
  }
}


class EventList extends Component {
  render() {
    return (
      <ul className="collapsible" data-collapsible="expandable">
        <DateSeparator date={new Date()}/>
        <Event league="RMRG" title="Shitshowdown" address="Everywhere USA"
               eventId={83} callTime="5pm"/>
      </ul>
    );
  }
}

class EditProfile extends Component {
  render() {
    return (
      <span>Profile</span>
    );
  }
}

class Schedule extends Component {
  render() {
    return (
      <span>Schedule</span>
    );
  }
}

class ManageLeague extends Component {
  render() {
    return (
      <span>ManageLeague</span>
    );
  }
}

class App extends Component {
  render() {
    return (
      <div>
       <Navbar />

       <Switch>
       <Route path="/apply/:eventId" component={Apply} />
       <Route exact path='/profile' component={EditProfile} />
       <Route exact path='/profile' component={EditProfile} />
       <Route exact path='/schedule' component={Schedule} />
       <Route exact path='/manage' component={ManageLeague} />
       <Route exact path='/' component={EventList} />
       </Switch>
       </div>
    );
  }
}
export default App;
