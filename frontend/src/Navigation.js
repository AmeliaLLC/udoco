/* global jQuery*/
import React, { Component } from 'react';
import { Link } from 'react-router-dom';


class Navbar extends Component {
  componentDidMount() {
    jQuery('.button-collapse').sideNav();
    jQuery('.collapsible').collapsible();
  }
  closeSide(){
    jQuery('.button-collapse').sideNav('hide');
  }
  render() {
    return (
      <div className="navbar-fixed">
        <nav className="nav-extended blue-grey darken-4 navbar-fixed">
          <div className="nav-wrapper">
            <Link to="/" className="brand-logo center">UDO CO</Link>
            <a href="#hambarglar" data-activates="hambarglar" className="button-collapse">
              <i className="material-icons">menu</i>
            </a>

            <ul className="right">


            {this.props.button?(
                <li>


                    {this.props.button.to?(<Link to={this.props.button.to}>
                      <i className="left material-icons">{this.props.button.icon}</i>
                      <span className=" hide-on-med-and-down">{this.props.button.text}</span>
                    </Link>):null}

                    {this.props.button.action?(<a onClick={this.props.button.action}>
                      <i className="left material-icons">{this.props.button.icon}</i>
                      <span className=" hide-on-med-and-down">{this.props.button.text}</span>
                    </a>):null}


                </li>
            )
            :null}

            {this.props.user && (<li className="hide-on-med-and-down">
              <Link to="/feedback" onClick={this.closeSide}>
                <i className="left material-icons">lightbulb_outline</i>Feedback
              </Link>
            </li>)}

            {this.props.user &&
              (<li className="hide-on-med-and-down">
                <a href="/logout/?next=/"><i className="left material-icons">exit_to_app</i>Logout</a>
              </li>)
            }


            </ul>
            {this.props.user !== null ? (
            <ul id="nav-non-mobile" className="left hide-on-med-and-down">
              <li>
                  <Link to="/profile">
                    <i className="left material-icons">perm_identity</i>Profile
                  </Link>
              </li>
              <li>
                  <Link to="/schedule">
                    <i className="left material-icons">today</i>My Schedule
                  </Link>
              </li>

              {this.props.user.league !== null &&
              <li>
                  <Link to="/league">
                    <i className="left material-icons">date_range</i>Manage League Events
                  </Link>
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
                  <Link to="/profile" onClick={this.closeSide}>
                    <i className="material-icons">perm_identity</i>Profile
                  </Link>
              </li>
              <li>
                  <Link to="/schedule" onClick={this.closeSide}>
                    <i className="material-icons">today</i>My Schedule
                  </Link>
              </li>
              {this.props.user.league !== null &&
              <li>
                  <Link to="/league" onClick={this.closeSide}>
                    <i className="material-icons">date_range</i>Manage League Events
                  </Link>
              </li>
              }

              {this.props.user && (<li>
                <Link to="/feedback" onClick={this.closeSide}>
                  <i className="left material-icons">lightbulb_outline</i>Feedback
                </Link>
              </li>)}

              <li>
                  <a href="/logout/?next=/">
                    <i className="material-icons">exit_to_app</i>Logout
                  </a>
              </li>
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
    </div>
    );
  }
}

export { Navbar };
