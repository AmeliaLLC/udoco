import 'materialize-css/dist/css/materialize.css';
import * as React from 'react';
import { Route, Switch } from 'react-router-dom';

import './App.css';
import { BaseURL } from './config';
import EventApply from './views/EventApply';
import EventEdit from './views/EventEdit';
import Events from './views/Events';
import EventSchedule from './views/EventSchedule';
import Feedback from './views/Feedback';
import League from './views/League';
import Profile from './views/Profile';
import Schedule from './views/Schedule';

interface IAppState {
    user?: any;
}

type AppState = Readonly<IAppState>;

class App extends React.Component<object, AppState> {
  public readonly state: AppState = {user: undefined}

  public componentWillMount() {
    fetch(`${BaseURL}/api/me`, {credentials: 'include'})
      .then(response => {
        if (response.status === 401) {
          return new Promise((resolve, reject) => resolve(undefined));
        }
        return response.json();
      })
      .then((data) => {
        this.setState({user: data});
      });
  }

  public render(): JSX.Element {
    const { user } = this.state;
    return (
      <div>

        <Switch>
          <Route exact={true} path='/' render={(props)=>(<Events {...props} user={user}/>)}/>

          <Route exact={true} path='/feedback' render={(props)=>(<Feedback {...props} user={user}/>)}/>
          <Route exact={true} path='/league' render={(props) => <League {...props} user={user}/>} />
          <Route exact={true} path='/profile' render={(props)=>(<Profile {...props} user={user}/>)} />
          <Route exact={true} path='/schedule' render={(props) => <Schedule {...props} user={user}/>} />

          <Route exact={true} path='/games/new' render={(props)=>(<EventEdit {...props} user={user}/>)} />

          <Route exact={true} path="/games/:gameId(\d+)" render={(props)=>(<Events {...props} user={user}/>)} />
          <Route exact={true} path="/games/:gameId(\d+)/apply" render={(props)=>(<EventApply {...props} user={user}/>)} />
          <Route exact={true} path='/games/:gameId(\d+)/edit' render={(props)=>(<EventEdit {...props} user={user}/>)} />
          <Route exact={true} path='/games/:gameId(\d+)/schedule' render={(props)=>(<EventSchedule {...props} user={user}/>)} />
        </Switch>
    </div>
    );
  }
}

export default App;
