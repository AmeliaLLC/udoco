import * as M from 'materialize-css/dist/js/materialize';
import * as moment from 'moment';
import * as React from 'react';
import { Redirect } from 'react-router';
import { RouteComponentProps } from 'react-router-dom';

import Navbar from "../components/Navbar";
import { BaseURL } from '../config';
import { IEventModel } from '../models/Event';
import { IURLParams } from '../types';
import { getCSRFToken } from '../util';

interface IEventEditProps extends RouteComponentProps<IURLParams> {
    user: any;
}

interface IEventEditState {
    date: Date;
    location: string;
    redirect: boolean;
    title: string;

    datepicker?: any;
    timepicker?: any;
}

export default class EventEdit extends React.Component<IEventEditProps, IEventEditState> {

    private datepicker: M.Datepicker;
    private timepicker: M.Timepicker;

    constructor(props: IEventEditProps) {
        super(props);

        this.state = {
            date: new Date(),
            location: '',
            redirect: false,
            title: '',
        };
    }

    public componentWillMount() {
        if (this.props.match.params.gameId !== undefined) {
            fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}`,{
                credentials: 'include',
                headers: {
                    'Content-type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                method: 'GET',
            })
            .then(response=>response.json())
            .then((data)=>{
                this.setState({
                    date: new Date(data.start),
                    location: data.location,
                    title: data.title,
                })
            });
        }
    }

    public componentDidMount() {
        const datepickerElems = document.querySelectorAll('.datepicker');
        const datepickerOptions = {
            autoClose: true,
            close: 'Ok',
            defaultDate: new Date(),
            format: 'dd mmm yyyy',
            minDate: new Date(),
            onSelect: this.updateDate.bind(this),
            selectMonths: true,
            selectYears: 2,
            showClearBtn: false,
            today: 'Today',
            yearRange: 2,
        };
        this.datepicker = M.Datepicker.init(datepickerElems, datepickerOptions)[0];

        const timepickerElems = document.querySelectorAll('.timepicker');
        const timepickerOptions = {
            autoClose: true,
            defaultTime: "19:00",
            onSelect: this.updateTime.bind(this),
            showClearBtn: false,
            twelveHour: false,
            vibrate: true,
        };
        this.timepicker = M.Timepicker.init(timepickerElems, timepickerOptions)[0];
    }

    public componentDidUpdate() {
        M.updateTextFields();

        if (this.state.date > new Date()) {
            this.datepicker.date = this.state.date;
            this.timepicker.time = moment(this.state.date).format('HH:mm');
        }
    }

    public updateName(e) {
        this.setState({title: e.target.value});
    }

    public updateLocation(e) {
        this.setState({location: e.target.value});
    }

    public updateTime(newHour: number, newMinute: number) {
        const current = this.state.date;
        current.setHours(newHour);
        current.setMinutes(newMinute);
        current.setMilliseconds(0);
        this.setState({date: current});
    }

    public updateDate(newDate: Date) {
        const current = this.state.date;
        current.setFullYear(newDate.getFullYear());
        current.setMonth(newDate.getMonth());
        current.setDate(newDate.getDate());
        this.setState({date: current});
    }

    public save() {
        const eventEdit = {
            location: this.state.location,
            start: this.state.date.toISOString(),
            title: this.state.title,
        };

        let url = `${BaseURL}/api/games`;
        let method = 'POST';
        if (this.props.match.params.gameId !== undefined) {
            url = `${BaseURL}/api/games/${this.props.match.params.gameId}`;
            method = 'PATCH';
        }

        fetch(url, {
            body: JSON.stringify(eventEdit),
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            method,
        })
        .then(response=>response.json())
        .then((data)=>{
            M.toast('Changes have been saved.', 2000);
            this.setState({redirect:true});
        })
        .catch((error)=>{
            console.error(error);
        });
    }

    public render() {
        return (
            <div>
                <Navbar user={this.props.user}/>
                <div className ="row">

                    <div className="row">
                        <div className="input-field col s12 m6">
                            <input onChange={this.updateName.bind(this)} id="eventName" type="text" value={this.state.title}/>
                            <label htmlFor="eventName">Event Name</label>
                        </div>
                    </div>

                    <div className="row">
                        <div className="input-field col s12 m6">
                            <input  id="eventLocation" type="text" onChange={this.updateLocation.bind(this) } value={this.state.location} />
                            <label htmlFor="eventLocation">Event Location</label>
                        </div>
                    </div>

                    <div className="row">
                        <div className="input-field col s12 m6">
                            <input id="eventDate" type="text" className="datepicker" value={this.state.date > new Date() ? moment(this.state.date).format('DD MMM YYYY') : ''}/>
                            <label htmlFor="eventDate">Event date</label>
                        </div>
                    </div>

                    <div className="row">
                        <div className="input-field col s12 m6">
                            <input id="eventTime" className="timepicker" value={this.state.date > new Date() ? moment(this.state.date).format('HH:mm') : ''} />
                            <label htmlFor="eventTime" className={this.state.date > new Date() ? 'active': ''}>Start time</label>
                        </div>
                    </div>

                    <div className="row">
                        <button className={"waves-effect waves-light btn blue-grey darken-4 col s12 m6" + ((this.state.title.length < 1 || this.state.location.length < 1 || this.state.date < new Date()) ? ' disabled' : '')} type="submit" onClick={this.save.bind(this)}>save event</button>
                    </div>

                </div>
                {this.state.redirect && (<Redirect to="/"/>)}
            </div>
        )
    }
}
