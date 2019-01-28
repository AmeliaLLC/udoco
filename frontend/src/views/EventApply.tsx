import * as M from 'materialize-css/dist/js/materialize';
import * as React from "react";
import { Link, Redirect, RouteComponentProps } from 'react-router-dom';

import Navbar from "../components/Navbar";
import { getCSRFToken } from '../util';

interface IPreferenceProps {
    change: any; // func
    value: number;
    index: number;
}
interface IPreferenceState {
    value: number;
}

const enum Position {
    HR,
    IPR,
    JR,
    OPR,
    HNSO = 5,
    PLT,
    JT = 9,
    SK,
    SO,
    PBM,
    PBT,
}

const PreferenceList = [
  {value: -1, label: 'Choose your option'},
  {value: -100, label: '- Skating positions -'},
  {value: Position.HR, label: 'Head ref'},
  {value: Position.IPR, label: 'Inside pack ref'},
  {value: Position.JR, label: 'Jam ref'},
  {value: Position.OPR, label: 'Outside pack ref'},

  {value: -101, label: '- Non-skating positions -'},
  {value: Position.HNSO, label: 'Head NSO'},
  {value: Position.PLT, label: 'Penalty/Lineup tracker'},
  {value: Position.JT, label: 'Jam time'},
  {value: Position.SK, label: 'Scorekeeper'},
  {value: Position.SO, label: 'Scoreboard operator'},
  {value: Position.PBM, label: 'Penalty box manager'},
  {value: Position.PBT, label: 'Penalty box timer'},
];

class Preference extends React.Component<IPreferenceProps, IPreferenceState> {

    public constructor(props: IPreferenceProps) {
        super(props);

        this.state = {
          value: props.value
        };
    }

    public onChange(evt) {
        this.props.change(this.state.value, evt.target.value);
        this.setState({value: evt.target.value});
    }

    public render() {
        /* It would be nice to re-work the drop-down each time a preference is
         * set so that users couldn't select the same item multiple times. It
         * will get filtered out on submit, but some consideration of
         * friendlier UIs is warranted.
         */
        return (
      <div className="row">
        <div className="input-field col s12 m12 l6 xl6">
          <select className="browser-default" name="preference[]" onChange={this.onChange.bind(this)} value={this.state.value}>
            {PreferenceList.map((item) => {
              return (
            <option key={`${this.props.index}.${item.value}`} value={item.value}>{item.label}</option>
          )
        })}
          </select>
        </div>
      </div>
        );
    }
}

interface IEventApplyRouterProps {
    gameId: string;
}
interface IEventApplyProps extends RouteComponentProps<IEventApplyRouterProps> {
    user?: any;
}

const DefaultEventApplyState = {
    email: '',
    event: null,
    name: '',
    notes: '',
    preferences: [-1],
    redirect: false
};
interface IEventApplyState {
    email: string;
    event?: any;
    name: string;
    notes: string;
    preferences: number[];
    redirect: boolean;
}

export default class EventApply extends React.Component<IEventApplyProps, IEventApplyState> {
    public readonly state: IEventApplyState = DefaultEventApplyState;

    public constructor(props: IEventApplyProps) {
        super(props);
    }

    public render() {
        return (
      <div>
      <Navbar user={this.props.user}/>
        <div className="row">
        {this.state.redirect?<Redirect to={{pathname: '/'}}/>:null}
          {(this.state.event !== null &&
          <form className="col s12">
            <h5 className="center">{this.state.event.title}</h5>
            <div className="row">
              <div className="input-field col">
                Please select your staffing preferences, starting with your top
                choice, continuing on to your last choice. You may choose as many
                positions as preferences as you would like.
              </div>
            </div>
            {(this.props.user === undefined &&
              <div className="row">
                <div className="input-field col s12 m6">
                  <input placeholder="" id="name" type="text" className="validate" value={this.state.name} onChange={this.onNameChange.bind(this)} />
                  <label htmlFor="name">Derby name</label>
                </div>
              </div>
            )}
            {(this.props.user === undefined &&
              <div className="row">
                <div className="input-field col s12 m6">
                  <input placeholder="" id="email" type="email" className="validate" value={this.state.email} onChange={this.onEmailChange.bind(this)} />
                  <label htmlFor="email">Email address</label>
                </div>
              </div>
            )}
            {this.state.preferences.map((item, idx) => (
              <Preference change={this.onChange.bind(this)} value={item} index={idx} key={idx}/>
            ))}

            <div className="row">
              <div className="input-field col s12 m6">
                <label>Additional Notes</label>
                <textarea onChange={this.updateNotes.bind(this)}  className="materialize-textarea"/>
              </div>
            </div>

            {this.props.user !== undefined && (
            <div className="row">
                <div className="col s12 m6">
                    If accepted, you'll recieve an email at {this.props.user.email}. If
                    this is not your desired email address, <a href="/profile">edit
                    your profile</a> and set your preferred email address.
                </div>
            </div>
            )}

            <div className="row">
              <div className="input-field col s12">
                <a onClick={this.onApply.bind(this)} className="center waves-effect waves-light btn blue-grey darken-4 col s12 m6">apply</a>
              </div>
            </div>
          </form>
          )}
          {(this.state.event === null &&
          <div className="col s6">
            Event not found. Please <a href="/">return to the events listing</a>
          </div>
          )}
        </div>
      </div>
    );
    }

    public onApply(evt) {
        evt.preventDefault();

        let url = `/api/games/${this.props.match.params.gameId}/applications/`;
        const preferences = this.state.preferences.filter((item) => item >= 0);
        if (!preferences.length) {
          M.toast({
              displayLength: 1000,
              html: 'Please choose at least one position.'
          });
          return;
        }
        let body = {
            email: '',
            name: '',
            notes: this.state.notes,
            preferences
        };

        if (this.props.user === undefined) {  // Loser application
            if (this.state.name === '' || this.state.email === '' || preferences.length === 0) {
                M.toast({
                    displayLength: 1000,
                    html: 'You must fill out all fields to apply'
                });
                return;
            }
            url = `/api/games/${this.props.match.params.gameId}/lapplications/`;
            body = {
                email: this.state.email,
                name: this.state.name,
                notes: this.state.notes,
                preferences
            };
        }

        fetch(url, {
            body: JSON.stringify(body),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'POST'
        })
        .then((response) => {
            if (response.status === 409) {
                M.toast({
                    displayLength: 10000,
                    html: 'You cannot apply to this event at this time.'
                });
            } else if (response.status === 201) {
                M.toast({
                    displayLength: 10000,
                    html: 'Your application has been received.'
                });
                this.setState({redirect: true});
            }
        })
        .catch((err) => {
            console.error(err);
            M.toast({
                displayLength: 10000,
                html: 'An unknown error has occurred.'
            });
        });
    }

    public onChange(oldValue, newValue) {
        /* There's a funny thing here: we always need to preserve the last item as
         * the empty object. This hack where we filter it out and then push it again
         * is how we do that. I'm so sorry. I didn't want to. Blame react, maybe?
         *
         * There is a bug here when preferences are deselected. I think it's also
         * a react issue, but IDGAF.
         */
        let preferences = this.state.preferences.filter((item) => (item >= 0));
        if (oldValue < 0) { // New value
            preferences.push(newValue);
        } else if (newValue >= 0) {  // Swapped value
            preferences[preferences.indexOf(oldValue)] = newValue;
        } else {  // Removed value
            preferences = preferences.filter((item) => item !== oldValue);
        }
        preferences.push(-1);
        this.setState({preferences});
    }

    public onNameChange(evt) {
        evt.preventDefault()
        this.setState({name: evt.target.value});
    }

    public onEmailChange(evt) {
        evt.preventDefault();
        this.setState({email: evt.target.value});
    }

    public updateNotes(evt) {
        evt.preventDefault();
        this.setState({notes: evt.target.value})
    }

    public componentWillMount() {
        fetch(`/api/games/${this.props.match.params.gameId}`, {credentials: 'include'})
        .then((response) => (response.json()))
        .then((data) => { this.setState({event: data}); })
        .catch((err) => {
            console.error(err);
            M.toast({
                completeCallback: () => { window.location.href = '/'; },
                displayLength: 1000,
                html: 'An unknown error has occurred.',
            });
        })
    }

    public componentDidMount() {
        M.FormSelect.init(document.querySelector('select'), {});
    }
}
