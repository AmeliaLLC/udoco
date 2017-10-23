/* global jQuery */
import React from 'react';
import moment from 'moment';
import { Redirect } from 'react-router-dom';
import { BaseURL } from './config.js';
import { getCSRFToken } from './utils.js';
import { Navbar } from './Navigation.js';
import TimePicker from 'material-ui/TimePicker';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'
import getMuiTheme from 'material-ui/styles/getMuiTheme';

const muiTheme = getMuiTheme({
  palette: {
    textColor: '#424242',
    backgroundColor: '#424242',
    pickerHeaderColor: 'black',
    primary1Color: 'black'
  }
});



export default class NewEvent extends React.Component {
  constructor(props){
    super(props);
    this.state={
      eventName: null,
      eventDate: null,
      eventTime: null,
      eventLocation: null,
      redirect: false
    };
  }
  componentWillMount=()=>{
    console.log(this.props);
  }
  componentDidMount(){
    jQuery('.datepicker').pickadate({
      selectMonths: true, // Creates a dropdown to control month
      selectYears: 15, // Creates a dropdown of 15 years to control year,
      today: 'Today',
      clear: 'Clear',
      close: 'Ok',
      closeOnSelect: false,
      onSet: this.updateEventDate
    });
  }

  updateEventTimeExp = (event, time)=>{
    time = moment(time).format('HH:mm');
    this.setState({eventTime: time});
  }

  updateEventName = () => {
    this.setState({eventName: this.refs.eventName.value});
  }

  updateEventDate = (date) => {
    date = date.select;
    date = new Date(date);
    date = date.toString();
    this.setState({eventDate: date});
  }

  updateEventLocation = () => {
    this.setState({eventLocation: this.refs.eventLocation.value});
  }

  updateEventTime = () => {
    let time = this.refs.eventTime.value;
    this.setState({eventTime: time});
  }

  submitEvent = (event) => {
    event.preventDefault();
    if(this.validate()){
      let body = {
        location: this.state.eventLocation,
        title: this.state.eventName,
        start: moment(this.getDateTime()).toISOString()
      };
      let url = `${BaseURL}/api/games`;
      fetch(url, {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(body),
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-type': 'application/json'
        }
      })
      .then( (response) => (response.json()) )
      .then((data) => {
        this.setState({redirect: true});
      })
      .catch((error)=>{
        console.error(error);
      });
    }else{
      //if the form isn't valid
    }
  }
  getDateTime = () => {
    let dateTime = this.state.eventDate.split(' ');
    let hours = dateTime[4].split(':');
    let timeSplit = this.state.eventTime.split(':')
    hours[0] = timeSplit[0];
    hours[1] = timeSplit[1]
    hours = hours.join(':');
    dateTime[4] = hours;
    dateTime = dateTime.join(' ');
    return dateTime;
  }

  validate = () => {
    for (let item in this.state) {
      if(!this.state[item] && item !== 'redirect') return false;
    }
    return true;
  }

  render(){
    return (
      <div>
      <Navbar user={this.props.user}/>
      {this.state.redirect?<Redirect to={{pathname: "/league"}}/>:null}
        <div className = "row">


          <div className="row">
            <div className="input-field col s12 m6">
              <input onChange={this.updateEventName} ref="eventName" id="eventName" type="text"/>
              <label htmlFor="eventName">Event Name</label>
            </div>
          </div>


          <div className="row">
            <div className="input-field col s12 m6">
              <input id="eventDate" type="text" className="datepicker"/>
              <label htmlFor="eventDate">Starting Date</label>
            </div>
          </div>

          <div className="row">
            <div className="input-field col s12 m6">
              <MuiThemeProvider muiTheme={muiTheme}>
                <TimePicker hintText="Start Time" onChange={this.updateEventTimeExp} minutesStep={15} textFieldStyle={{
                  width: '100%',
                  color: 'black'
                }}/>
                </MuiThemeProvider  >
            </div>
          </div>

          <div className="row">
            <div className="input-field col s12 m6">
              <input id="eventLocation" type="text" ref="eventLocation" onChange={this.updateEventLocation}/>
              <label htmlFor="eventLocation">Location</label>
            </div>
          </div>

          <div className="row">
            <button className="waves-effect waves-light btn blue-grey darken-4 col s12 m6" type="submit" onClick={this.submitEvent}>create event</button>
          </div>
        </div>
      </div>
    )
  }
}

/*
event nav
start date
start time
location

*/
