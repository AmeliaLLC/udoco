import * as M from 'materialize-css/dist/js/materialize';
import * as React from "react";
import { RouteComponentProps } from 'react-router-dom';

import Navbar from '../components/Navbar';
import Roster from '../components/Roster';
import { BaseURL } from '../config';
import { IURLParams } from '../types';
import { getCSRFToken } from '../util';

import question from '../images/question.svg';

interface IEventScheduleProps extends RouteComponentProps<IURLParams> {
    user?: object;
}

interface IEventScheduleState {
    applications: any[];
    event: any;
    lapplications: any[];
    rosters: any[];
}

export default class EventSchedule extends React.Component<IEventScheduleProps, IEventScheduleState> {

    private tabs: string;

    constructor(props: IEventScheduleProps) {
        super(props);

        this.state = {
            applications: [],
            event: { complete: false },
            lapplications: [],
            rosters: [],
        };
    }

    public componentWillMount() {
        fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}/applications`, {
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
            },
            method: 'GET',
        })
        .then((response) => response.json() )
        .then((applications) => {
            this.setState({applications});
        });

        fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}/lapplications`, {
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
            },
            method: 'GET',
        })
        .then((response) => response.json() )
        .then((lapplications) => {
            this.setState({lapplications});
        });

        fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}/rosters`,{
          credentials: 'include',
          headers: {
            'Content-type': 'application/json'
          },
          method: 'GET',
        })
        .then((response)=>(response.json()))
        .then((rosters)=>{
          rosters.forEach((roster)=>{
            for(const position in roster){
              if(roster[position]===null){
                roster[position] = "";
              }
            }
          });
          this.setState({rosters});
        });
    }

    public componentDidUpdate() {
        const tabs = document.getElementById('tabs');
        if (tabs !== null) {
            const options = {
                // Can't use swipeable because it doesn't draw the height
                // of the tab content correctly.
                // swipeable: true,
            };
            M.Tabs.init(tabs, options);
        }

        const elems = document.querySelectorAll('.modal');
        M.Modal.init(elems, {});
    }

    public newRoster() {
        const newRoster = {};
        fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}/rosters/`,{
            body: JSON.stringify(newRoster),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'POST',
        })
        .then((response)=>{
            return response.json()
        })
        .then((createdRoster)=>{
            for (const position in createdRoster){
                if (createdRoster[position] === null) {
                    createdRoster[position] = '';
                }
            }
            const copy = this.state.rosters.slice();
            copy.push(createdRoster);
            this.setState({rosters: copy});
        });
    }

    public updateRoster(index: number, role: string, userId: string) {
        const copy = this.state.rosters.slice();
        copy[index][role] = userId;
        this.setState({rosters:copy});
    }

    public removePosition(index: number, role: string) {
        const copy = this.state.rosters.slice();
        copy[index][role] = '';
        this.setState({rosters:copy});
    }

    public render() {
        return (
            <div>
                <Navbar user={this.props.user} />

                <div className="row">
                    <div className="col s12">
                        <ul id="tabs" className="tabs tabs-fixed-width">
                            <li className="tab"><a className="active" href="#applications">Applications</a></li>
                            {this.state.rosters.map((roster, index) => (
                            <li key={index} className="tab"><a href={"#roster"+index}>Roster {index+1}</a></li>
                            ))}
                            <li className="tab"><a href="#" onClick={this.newRoster.bind(this)}>Add new roster</a></li>
                        </ul>
                    </div>

                    <div id="applications" className="col s12">
                        {(this.state.applications.length === 0 && this.state.lapplications.length === 0 &&
                        <p>There are no applicants for this event</p>
                        )}
                        {((this.state.applications.length !== 0 || this.state.lapplications.length !== 0) &&
                        <ul className="collection">
                            {this.state.applications.map((application, index) => (
                            <li className="collection-item avatar" key={index}>
                                <img src={application.avatar} alt={application.display_name} title={application.display_name} className="circle"/>
                                <span className="title">{application.display_name}</span>
                                <p>{application.preferences.map((preference, index) => (<span className="chip" key={index}>{preference}</span>))}<br /><span className="notes">{application.notes}</span></p>
                            </li>
                            ))}
                            {this.state.lapplications.map((application, index) => (
                            <li className="collection-item avatar" key={index}>
                                <img src={question} alt={application.derby_name} title={application.derby_name} className="circle"/>
                                <span className="title">{application.derby_name}</span>
                                <p>{application.preferences.map((preference, index) => (<span className="chip" key={index}>{preference}</span>))}<br /><span className="notes">{application.notes}</span></p>
                            </li>
                            ))}
                        </ul>
                        )}
                    </div>
                    {this.state.rosters.map((roster, index) => (
                    <Roster key={index} applications={this.state.applications} lapplications={this.state.lapplications} index={index} roster={roster} updateRoster={this.updateRoster.bind(this)} removePosition={this.removePosition.bind(this)} saveRoster={this.saveRoster.bind(this)} deleteRoster={this.deleteRoster.bind(this)} />
                    ))}
                    {!this.state.event.complete && (
                    <div>
                        <button data-target="finalizeModal" className="btn modal-trigger waves-effect waves-light btn grey lighten-1 col s12 m6">Finalize event</button>

                        <div id="finalizeModal" className="modal">
                            <div className="modal-content">
                                <h4>Finalize event?</h4>
                                <p>
                                    This will make all rosters notify all applicants.
                                    After finalizing the rosters, these rosters should
                                    only be changed in extreme circumstances.
                                    Are you sure you want to do this?
                                </p>
                            </div>
                            <div className="modal-footer">
                                <a href="#!" className="modal-close waves-effect waves-green btn-flat">Cancel</a>
                                <a href="#!" className="modal-close waves-effect waves-green btn-flat" onClick={this.finalizeEvent.bind(this)}>Finalize</a>
                            </div>
                        </div>
                    </div>
                    )}
                </div>
            </div>
        );
    }

    private saveRoster(index: number) {
        const roster = Object.assign({}, this.state.rosters[index]);
        for (const position in roster) {
            if (roster[position] === '') {
                roster[position] = null;
            }
        }

        const id = roster.id;
        delete roster.id;
        const url = `${BaseURL}/api/games/${this.props.match.params.gameId}/rosters/${id}/`;
        fetch(url, {
            body: JSON.stringify(roster),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'PUT',
        })
        .then((response) => (response.json()))
        .then((updateRoster) => M.toast({ displayLength: 1500, html: 'Roster saved'}));
    }

    private deleteRoster(index: number) {
        const roster = this.state.rosters[index];
        const url = `${BaseURL}/api/games/${this.props.match.params.gameId}/rosters/${roster.id}/`;
        fetch(url, {
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'DELETE',
        })
        .then(() => {
            const copy = this.state.rosters.slice();
            copy.splice(index, 1);
            this.setState({rosters: copy}, () => {
                M.toast({displayLength: 1500, html: 'Roster deleted'});
            });
        });
    }

    private finalizeEvent() {
        fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}`, {
            body: JSON.stringify({complete: true}),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'PATCH',
        })
        .then(response=>response.json())
        .then((response)=>{
            window.location.href = '/';
        });
    }
}
