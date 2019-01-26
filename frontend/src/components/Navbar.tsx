import * as M from 'materialize-css/dist/js/materialize';
import * as React from "react";
import { Link } from 'react-router-dom';

interface IButton {
    action?: any;
    icon: string;
    text: string;
    to: string;
}

interface INavbarProps {
    user?: any;
    button?: IButton;
}

class Navbar extends React.Component <INavbarProps, {}> {
    private sideNav: any;

    public constructor(props: INavbarProps) {
        super(props);
    }

    public componentDidMount() {
        const elems = document.querySelectorAll('.sidenav');
        this.sideNav = M.Sidenav.init(elems, {})[0];
    }

    public render() {
        return (
            <div className="navbar-fixed">
                <nav className="blue-grey darken-4">
                    <div className="nav-wrapper">
                        <Link to="/" className="brand-logo center hide-on-med-and-down">United Derby Officials</Link>
                        <Link to="/" className="brand-logo center hide-on-large-only">UDO CO</Link>
                        <a href="#hambarglar" data-target="hambarglar" className="sidenav-trigger"><i className="material-icons">menu</i></a>

                        {this.props.user && (<ul className="right">
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
                            ):null}
                            <li className="hide-on-med-and-down">
                                <Link to="/feedback">
                                    <i className="left material-icons">lightbulb_outline</i>Feedback
                                </Link>
                            </li>
                            <li className="hide-on-med-and-down">
                                <a href="/logout/?next=/"><i className="left material-icons">exit_to_app</i>Logout</a>
                            </li>
                        </ul>)}

                        <ul id="nav-non-mobile" className="left hide-on-med-and-down">
                            {this.props.user !== undefined ? (
                            <span>
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
                            </span>
                            ) : (
                            <li>
                                <a href="/auth/login/facebook">
                                    <i className="left material-icons">lock_outline</i>Log in
                                </a>
                            </li>
                            )}
                        </ul>
                    </div>
                </nav>

                <ul id="hambarglar" className="sidenav">
                    {this.props.user !== undefined ? (
                    <span>
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
                        <li>
                            <Link to="/feedback">
                                <i className="left material-icons">lightbulb_outline</i>Feedback
                            </Link>
                        </li>
                        <li>
                            <a href="/logout/?next=/"><i className="left material-icons">exit_to_app</i>Logout</a>
                        </li>
                    </span>
                    ) : (
                    <li>
                        <a href="/auth/login/facebook">
                            <i className="left material-icons">lock_outline</i>Log in
                        </a>
                    </li>
                    )}
                </ul>
            </div>
        );
    }
}

export default Navbar;
