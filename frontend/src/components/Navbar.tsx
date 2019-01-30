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
}

class Navbar extends React.Component <INavbarProps, {}> {
    private sideNav: any;
    private dropdown: any;

    public constructor(props: INavbarProps) {
        super(props);
    }

    public componentDidMount() {
        const elems = document.querySelectorAll('.sidenav');
        this.sideNav = M.Sidenav.init(elems, {})[0];
    }

    public componentDidUpdate() {
        const dropdowns = document.querySelectorAll('.dropdown-trigger');
        const options = {
            constrainWidth: false,
        };
        this.dropdown = M.Dropdown.init(dropdowns, options)[0];
    }

    public render() {
        return (
            <div className="navbar-fixed">

                {this.props.user !== undefined && (
                <ul id="auth-dropdown" className="dropdown-content">
                    <li><Link to="/profile">
                        <i className="left material-icons">perm_identity</i>Edit Profile
                    </Link></li>
                    <li><Link to="/schedule">
                        <i className="left material-icons">today</i>My Schedule
                    </Link></li>
                    {this.props.user.league !== null &&
                    <li><Link to="/games/new">
                            <i className="left material-icons">add_circle_outline</i>Add New Event
                    </Link></li>
                    }
                    {this.props.user.league !== null &&
                    <li><Link to="/league">
                            <i className="left material-icons">date_range</i>Manage League
                    </Link></li>
                    }
                    <li><Link to="/feedback">
                        <i className="left material-icons">lightbulb_outline</i>Feedback
                    </Link></li>

                    <li className="divider" />

                    <li><a href="/logout/?next=/">
                        <i className="left material-icons">exit_to_app</i>Logout
                    </a></li>
                </ul>
                )}

                <nav className="blue-grey darken-4">
                    <div className="nav-wrapper">
                        <Link to="/" className="brand-logo center hide-on-med-and-down">United Derby Officials</Link>
                        <Link to="/" className="brand-logo center hide-on-large-only">UDO CO</Link>
                        <a href="#hambarglar" data-target="hambarglar" className="sidenav-trigger"><i className="material-icons">menu</i></a>

                        {this.props.user !== undefined ? (
                        <ul id="nav-non-mobile" className="right hide-on-med-and-down">
                            <li className="hide-on-med-and-down"><a className="dropdown-trigger" href="#!" data-target="auth-dropdown">
                                <img src={this.props.user.avatar} alt="" title={this.props.user.display_name} className="circle non-mobile-profile"/>
                                {this.props.user.display_name}
                                <i className="material-icons right">arrow_drop_down</i>
                            </a></li>
                        </ul>
                        ) : (
                        <ul id="nav-non-mobile" className="right hide-on-med-and-down">
                            <li>
                                <a href="/auth/login/facebook">
                                    <i className="left material-icons">lock_outline</i>Log in
                                </a>
                            </li>
                        </ul>
                        )}
                    </div>
                </nav>

                <ul id="hambarglar" className="sidenav">
                    {this.props.user !== undefined ? (
                    <span>
                        <li className="z-depth-3">
                            <img src={this.props.user.avatar} alt="" title={this.props.user.display_name} className="circle mobile-profile"/>
                            {this.props.user.display_name}
                        </li>
                        <li>
                            <Link to="/profile">
                                <i className="left material-icons">perm_identity</i>Edit Profile
                            </Link>
                        </li>
                        <li>
                            <Link to="/schedule">
                                <i className="left material-icons">today</i>My Schedule
                            </Link>
                        </li>

                        {this.props.user.league !== null &&
                        <li><Link to="/games/new">
                            <i className="left material-icons">add_circle_outline</i>
                            Add New Event
                        </Link></li>
                        }
                        {this.props.user.league !== null &&
                        <li>
                            <Link to="/league">
                                <i className="left material-icons">date_range</i>
                                Manage League Events
                            </Link>
                        </li>
                        }
                        <li>
                            <Link to="/feedback">
                                <i className="left material-icons">lightbulb_outline</i>Feedback
                            </Link>
                        </li>
                        <li><div className="divider" /></li>
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
