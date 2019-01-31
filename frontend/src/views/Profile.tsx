import * as Materialize from "materialize-css";
import * as React from 'react';

import Navbar from "../components/Navbar";
import { BaseURL } from '../config';
import { getCSRFToken } from '../util';


interface IProfileProps {
    user: any;
}
interface IProfileState {
    user: any;
}


export default class Profile extends React.Component<IProfileProps, IProfileState> {

    constructor(props: IProfileProps) {
        super(props);

        this.state = {
            user: null,
        };
    }

    public componentWillMount() {
        const self = this;
        fetch(`${BaseURL}/api/me`, {credentials: 'include'})
        .then((response) => {
            return response.json();
        })
        .then((user) => {
            self.setState({user});
        })
        .catch(() => {
            console.warn('Not logged in');
        });
    }

    public onChange(e) {
        const user = this.state.user;
        user[e.target.id] = e.target.value;
        this.setState({user});
    }

    public onSave(e) {
        e.preventDefault();

        fetch(`${BaseURL}/api/me`, {
            body: JSON.stringify(this.state.user),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'PUT',
        })
        .then((response) => {
            Materialize.toast({
                displayLength: 1000,
                html: 'Your profile information has been saved.'
            });
        });
    }

    public componentDidUpdate() {
        Materialize.updateTextFields();
    }

    public render() {

    if (this.state.user === null) {
      return (
        <div className="row">
          <div className="col s6">
            Loading your settings
          </div>
        </div>
      );
    }

    return (
      <div>
      <Navbar user={this.props.user}/>
        <div className="row">
          <form className="col s12">
            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="display_name" type="text" className="validate" value={this.state.user.display_name} onChange={this.onChange.bind(this)} maxLength={254} />
                <label>Derby name</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="email" type="email" className="validate" value={this.state.user.email} onChange={this.onChange.bind(this)} maxLength={254} />
                <label>Preferred email address</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="league_affiliation" type="text" className="validate" value={this.state.user.league_affiliation} onChange={this.onChange.bind(this)} maxLength={254} />
                <label>League affiliation</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="game_history" type="text" className="validate" value={this.state.user.game_history} onChange={this.onChange.bind(this)} maxLength={200} />
                <label>Game history</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="phone_number" type="text" className="validate" value={this.state.user.phone_number} onChange={this.onChange.bind(this)} maxLength={16} />
                <label>Phone number</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="emergency_contact_name" type="text" className="validate" value={this.state.user.emergency_contact_name} onChange={this.onChange.bind(this)} maxLength={254} />
                <label>Emergency contact name</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <input placeholder="" id="emergency_contact_number" type="text" className="validate" value={this.state.user.emergency_contact_number} onChange={this.onChange.bind(this)} maxLength={16} />
                <label>Emergency contact phone number</label>
              </div>
            </div>

            <div className="row">
              <div className="input-field col s12 m6">
                <a className="center waves-effect waves-light btn blue-grey darken-4 col s12" onClick={this.onSave.bind(this)}>Save</a>
              </div>
            </div>

          </form>
        </div>
      </div>
    );
    }
}
