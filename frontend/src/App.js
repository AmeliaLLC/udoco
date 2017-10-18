/* global jQuery*/
import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import Apply from './Apply.js';
import { EventList } from './Events.js';
import './App.css';

class Navbar extends Component {
  componentDidMount() {
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

        {this.props.user !== null ? (
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
          {this.props.user.league != null &&
          <li>
              <a href="/manage">
                <i className="left material-icons">supervisor_account</i>Manage League
              </a>
          </li>
          }
        </ul>
        ) : (
        <ul id="nav-non-mobile" className="left hide-on-med-and-down">
          <li>
              <a href="/auth/login/facebook">
                <i className="left material-icons">lock_outline</i>Log in
              </a>
          </li>
        </ul>
        )}

        {this.props.user !== null ? (
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
          {this.props.user.league != null &&
          <li>
              <a href="/manage">
                <i className="material-icons">supervisor_account</i>Manage League
              </a>
          </li>
          }
        </ul>
        ) : (
        <ul id="hambarglar" className="side-nav">
          <li>
              <a href="/auth/login/facebook">
                <i className="material-icons">lock_outline</i>Log in
              </a>
          </li>
        </ul>
        )}
      </div>
    </nav>
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
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    };
  }

  componentWillMount() {
    const self = this;
    fetch('/api/me', {credentials: 'same-origin'}).then(response => {
      if (response.status === 401) {
        return;
      }
      self.setState({user: response.json()});
    });
  }

  render() {
    return (
      <div>
       <Navbar user={this.state.user}/>

       <Switch>
       <Route path="/apply/:eventId" component={Apply} />
       <Route exact path='/_profile' component={EditProfile} />
       <Route exact path='/_schedule' component={Schedule} />
       <Route exact path='/_manage' component={ManageLeague} />
       <Route exact path='/_' component={EventList} />
       </Switch>
       </div>
    );
  }
}
export default App;

