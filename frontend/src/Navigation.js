/* global jQuery*/
import React, { Component } from 'react';


class Navbar extends Component {
  componentDidMount() {
    jQuery('.button-collapse').sideNav();
    jQuery('.collapsible').collapsible();
  }
  render() {
    return (
    <nav className="nav-extended blue-grey darken-4">
      <div className="nav-wrapper">
        <a href="/_" className="brand-logo center">UDO CO</a>
        <a href="#hambarglar" data-activates="hambarglar" className="button-collapse">
          <i className="material-icons">menu</i>
        </a>

        {this.props.user !== null ? (
        <ul id="nav-non-mobile" className="left hide-on-med-and-down">
          <li>
              <a href="/_profile">
                <i className="left material-icons">perm_identity</i>Profile
              </a>
          </li>
          <li>
              <a href="/_schedule">
                <i className="left material-icons">today</i>My Schedule
              </a>
          </li>
          {this.props.user.league !== null &&
          <li>
              <a href="/_league">
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
          {this.props.user.league !== null &&
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

export { Navbar };