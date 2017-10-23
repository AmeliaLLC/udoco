import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import Apply from './Apply.js';
import { EventList } from './Events.js';
import { EditProfile } from './Profile.js';
import { Navbar } from './Navigation.js';
import { BaseURL } from './config.js';
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
       <Navbar user={this.state.user}/>

       <Switch>
         <Route path="/_apply/:eventId" component={Apply} />
         <Route path="/_apply/:eventId/luser" component={Apply} />
         <Route exact path='/_profile' component={EditProfile} />
         <Route exact path='/_league' render={(props) => <EventList {...props} league={true} />} />
         <Route exact path='/_schedule' render={(props) => <EventList {...props} schedule={true} />} />
         <Route exact path='/_' component={EventList} />
       </Switch>
     </div>
    );
  }
}
export default App;
