/* global jQuery */
/* global Materialize */
import React from 'react';
import { Redirect } from 'react-router';
import { Navbar } from './Navigation.js';
import { BaseURL } from './config.js';
import { getCSRFToken } from './utils.js';
import moment from 'moment';
import TimePicker from 'material-ui/TimePicker';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import './App.css';



const muiTheme = getMuiTheme({
  palette: {
    textColor: '#424242',
    backgroundColor: '#424242',
    pickerHeaderColor: 'black',
    primary1Color: 'black'
  }
});







export default class EditEvent extends React.Component{
  constructor (props){
    super(props);
    this.state = {
      title: null,
      dateTime: null,
      location: null,
      time: null,
      date: null,
      showDate: null,
      redirect: false
    }
  }
  componentWillMount = () =>{
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}`,{
      method: 'GET',
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then(response=>response.json())
    .then((data)=>{
      let showDate = moment(data.start.replace('Z', '')).format('DD MMMM, YYYY');
      let time = moment(data.start).format('HH:mm');
      this.setState({
        title: data.title,
        date: new Date(data.start),
        time: time,
        location: data.location,
        showDate: showDate
      })
    });
  }
  componentDidMount = () =>{
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
  updateEventName = () => {
    this.setState({title: this.refs.eventName.value});
  }
  updateEventLocation = () => {
    this.setState({location: this.refs.eventLocation.value});
  }
  updateEventTime = (event, time)=>{
    time = moment(time).format('HH:mm');
    this.setState({time});
  }
  updateEventDate = (date)=>{
    date = new Date(date.select);
    this.setState({date, showDate: this.refs.eventDate.value});
  }
  getDate = ()=>{
    let dateArray = this.state.date.toString().split(' ');
    dateArray[4] = this.state.time+":00";
    let dateString = dateArray.join(' ');
    let momentFormatted = moment(dateString).toISOString();
    return momentFormatted;
  }
  saveEvent = () =>{
    let start = this.getDate();
    let eventEdit = {
      location: this.state.location,
      title: this.state.title,
      start: start
    };
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}`,{
      method: 'PATCH',
      credentials: 'include',
      body: JSON.stringify(eventEdit),
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
        }
      })
      .then(response=>response.json())
      .then((data)=>{
        Materialize.toast('Changes have been saved.', 2000);
        this.setState({redirect:true});
      });
  }
  render(){
    return (
      <div>
        <Navbar user={this.props.user}/>
        <div className ="row">

        <div className="row">
          <div className="input-field col s12 m6">
            <input onChange={this.updateEventName} ref="eventName" id="eventName" type="text" value={this.state.title} placeholder="Event Name"/>
            <label htmlFor="eventName" className="active">Event Name</label>
          </div>
        </div>

        <div className="row">
          <div className="input-field col s12 m6">
            <input  id="eventLocation" type="text" ref="eventLocation" onChange={this.updateEventLocation} value={this.state.location} placeholder="Event Location"/>
            <label htmlFor="eventLocation" className="active">Event Location</label>
          </div>
        </div>

        <div className="row">
          <div className="input-field col s12 m6">
            <input ref="eventDate" id="eventDate" type="text" className="datepicker" value = {this.state.showDate}/>
          </div>
        </div>

        <div className="row">
          <div className="input-field col s12 m6">
            <MuiThemeProvider muiTheme={muiTheme}>
              <TimePicker hintText={this.state.time} onChange={this.updateEventTime} minutesStep={15} textFieldStyle={{
                width: '100%',
                color: 'black'
              }}/>
            </MuiThemeProvider>
          </div>
        </div>

        <div className="row">
          <button className="waves-effect waves-light btn blue-grey darken-4 col s12 m6" type="submit" onClick={this.saveEvent}>save event</button>
        </div>

        </div>
        {this.state.redirect && (<Redirect to="/"/>)}
      </div>
    )
  }
}
