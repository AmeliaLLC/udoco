import * as M from 'materialize-css/dist/js/materialize';
import * as moment from "moment";
import * as React from "react";
import { Link, RouteComponentProps } from 'react-router-dom';

import Navbar from "../components/Navbar";
import { BaseURL } from '../config';
import { IEventModel } from '../models/Event';
import { IURLParams } from '../types';
import { getCSRFToken } from '../util';

interface IEventProps extends RouteComponentProps<IURLParams> {
    cancelEvent: any;
    event: IEventModel;
    renderWithdraw: any;  // func
    user?: any;
}

class Event extends React.Component <IEventProps, {}> {
    constructor(props: IEventProps) {
        super(props);
    }

    public onWithdraw(e: any) {
        e.preventDefault();

        const url = `${BaseURL}/api/games/${this.props.event.id}/applications/0/`;
        fetch(url, {
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method: 'DELETE'
        })
        .then((response) => {
            if (response.status === 204) {
                M.toast({
                    displayLength: 1500,
                    html: 'You have withdrawn from this event.'
                });
                this.props.renderWithdraw(this.props.event.id);
            } else {
                M.toast({
                    displayLength: 1500,
                    html: 'An error has occurred. Unable to withdraw.'
                });
            }
        })
    }

    public render(): JSX.Element {
        const event = this.props.event;
        // XXX: rockstar (23 Jan 2019) - Ugh. IURLParams doesn't seem to
        // like typing gameId to being a number, so this conversion is
        // required.
        const gameId = Number(this.props.match.params.gameId);

    return (
      <li id={"event-"+event.id} className={gameId !== undefined && gameId === event.id ? "active" : ""}>
        <div className="collapsible-header">
          <div className="row marginLess">
            <div className="col s11 eventHeader">
              {event.league} presents - {event.title}
            </div>
            <div className="col s1">
              <p className="arrowHolder">
                <Link to={`/games/${event.id}`} title="direct game link">

                  <i className="right material-icons noRightLeft moveRightALittle" >chevron_right</i>
                </Link>
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
              <Link to={`/games/${event.id}/apply`} className="center waves-effect waves-light btn blue-grey darken-4 col s12">apply</Link>
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
                username/password. <a href={`/games/${event.id}/apply`}>I'd rather not use Facebook</a>
              </div>
            </div>
          </div>
          )}

        </div>
      </li>
    )}
}


interface IEventGroupProps extends RouteComponentProps<IURLParams> {
    cancelEvent: any;
    events: [IEventModel];
    label: string;
    renderWithdraw: any;  // func
    user?: any;
}

class EventGroup extends React.Component <IEventGroupProps, {}> {
    constructor(props: IEventGroupProps) {
        super(props);
    }

    public render(): JSX.Element {
      return (
        <ul className="collapsible">
          <li className="blue-grey lighten-4">{this.props.label}</li>
          {this.props.events.map((item) => {
            return (<Event {...this.props} key={item.id} event={item} renderWithdraw={this.props.renderWithdraw} cancelEvent={this.props.cancelEvent}/>);
          })}
        </ul>
      );
    }
}

interface IEventListProps extends RouteComponentProps<IURLParams> {
    user?: object;
}

const DefaultEventListState = {
    events: [],
    grouped_events: [],
    groups: [],
};
interface IEventListState {
    events: any[];
    groups: string[];
    grouped_events: any[];
};

class EventList extends React.Component <IEventListProps, IEventListState> {
    public readonly state: IEventListState = DefaultEventListState;
    protected endpoint = '';

    public constructor(props: IEventListProps) {
        super(props);
    }

    public componentWillReceiveProps(nextProps: IEventListProps) {
        this.componentWillMount();
    }

    public componentWillMount() {
        const self = this;
        const FORMAT = 'D MMM YYYY';
        fetch(this.endpoint, {credentials: 'include'})
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
            const newEvents = [];
            const groups: string[] = [];

            results.map((item) => {
                const date = moment(item.start);

                const key = date.format(FORMAT);
                if (newEvents[key] === undefined) {
                    groups.push(key);
                    newEvents[key] = [item];
                } else {
                    newEvents[key].push(item);
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
                grouped_events: newEvents,
                groups
            });
        })
        .catch((err) => console.warn('Failure fetching events: ', err));
    }

    public componentDidUpdate() {
        M.Collapsible.init(document.querySelectorAll('.collapsible'), {});
        M.Tooltip.init(document.querySelector('.tooltipped'), {});

        if (this.props.match.params.gameId !== undefined) {
            const target = document.getElementById('event-'+this.props.match.params.gameId);
            if (target !== null) {
                target.scrollIntoView({block: "center", inline: "nearest"});
            }
        }
    }


    public renderWithdraw(id: string) {
        const FORMAT = 'D MMM YYYY';
        const eventsCopy = this.state.events.slice();
        const groupedEventsCopy = Object.assign({}, this.state.grouped_events);
        const withdrawnEvent = eventsCopy.find((event)=>(event.id===id));
        const date = moment(withdrawnEvent.start).format(FORMAT);
        withdrawnEvent.can_apply = true;
        withdrawnEvent.has_applied = false;
        const groupedEventToUpdate = groupedEventsCopy[date].find((event)=>(event.id===id));
        groupedEventToUpdate.can_apply = true;
        groupedEventToUpdate.has_applied = false;
        this.setState({events: eventsCopy, grouped_events: groupedEventsCopy});
    }

    public cancelEvent(id: string) {
        return;
    }

    public getNavbar() {
        return (<Navbar user={this.props.user} button={undefined} />);
    }

    public render(): JSX.Element {
        return (
            <div>
                {this.getNavbar()}
                <section>
                    {this.state.groups.map((item) => { return (
                        <EventGroup {...this.props} key={item} label={item} renderWithdraw={this.renderWithdraw} events={this.state.grouped_events[item]} cancelEvent={this.cancelEvent}/>
                    )})}
                </section>
            </div>
        );
    }
}

export { EventList };
