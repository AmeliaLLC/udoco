import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import Apply from './Apply.js';
import { EventList } from './Events.js';
import { EditProfile } from './Profile.js';
import Feedback from './Feedback.js';
import { BaseURL } from './config.js';
import NewEvent from './NewEvent.js';
import ScheduleEvent from './ScheduleEvent';
import EditEvent from './EditEvent.js';
import Game from './Game.js';
import './App.css';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    };
  }

  componentWillMount() {
    const self = this;
    fetch(`${BaseURL}/api/me`, {credentials: 'include'})
      .then(response => {
        if (response.status === 401) {
          return new Promise((resolve, reject) => resolve(null));
        }
        return response.json();
      })
      .then((data) => {
        self.setState({user: data});
      });
  }

  render() {
    return (
      <div>

        <Switch >
          <Route exact path='/' render={(props)=>(<EventList {...props} league={false} user={this.state.user}/>)}/>

          <Route exact path='/feedback' render={(props)=>(<Feedback {...props} user={this.state.user}/>)}/>

          <Route exact path='/games/new' render={(props)=>(<NewEvent {...props} user={this.state.user}/>)} />

          <Route path='/games/:id/schedule' render={(props)=>(<ScheduleEvent {...props} user={this.state.user}/>)} />

          <Route path='/games/:id/edit' render={(props)=>(<EditEvent {...props} user={this.state.user}/>)} />

          <Route path="/games/:gameId" render={(props)=>(<Game {...props} user={this.state.user}/>)} />

          <Route path="/apply/:eventId" render={(props)=>(<Apply {...props} user={this.state.user}/>)} />

          <Route path="/apply/:eventId/luser" render={(props)=>(<Apply {...props} user={this.state.user}/>)} />

          <Route exact path='/profile' render={(props)=>(<EditProfile {...props} user={this.state.user}/>)} />

          <Route exact path='/league' render={(props) => <EventList {...props} league={true} user={this.state.user}/>} />

          <Route exact path='/schedule' render={(props) => <EventList {...props} schedule={true} user={this.state.user}/>} />

        </Switch>
    </div>
    );
  }
}
export default App;
