/* global Materialize */
import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from './Navigation.js';
import { BaseURL } from './config.js';
import { getCSRFToken } from './utils.js';
import moment from 'moment';
import './App.css';

export default class Game extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      game: {}
    }
  }
  withdrawApplication = (event)=>{
    event.preventDefault();
    const url = `${BaseURL}/api/games/${this.state.game.id}/applications/0/`;
    fetch(url, {
      credentials: 'include',
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then((response) => {
      if (response.status === 204) {
        Materialize.toast('You have withdrawn from this event.', 1500);
        this.matchGame();
      } else {
        Materialize.toast('An error has occurred. Unable to withdraw.', 1500);
      }
    })
  }
  componentWillMount = ()=>{
    this.matchGame();
  }
  matchGame = ()=>{
    fetch(`${BaseURL}/api/games/${this.props.match.params.gameId}`,{
      method: 'GET',
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then(response=>response.json())
    .then((game)=>{
      this.setState({game});
    });
  }
  render(){
    const game = this.state.game;
    return(
      <div>
        <Navbar user={this.props.user}/>

        <div className="row game-league-presents">
          <p className="center col s12 m6 game-league-presents">{game.league} presents</p>
        </div>
        <div className="row">
          <h1 className="center col s12 m6 game-leage-event-name">{game.title}</h1>
        </div>



        <div className="row">
          <div className="col s4">
            <b>Location</b>
          </div>
          <div className="col s8">
            {game.location}
          </div>
        </div>

        <div className="row">
          <div className="col s4">
            <b>Start time</b>
          </div>
          <div className="col s8">
            {`${moment(game.start).format('hh:mm a')}`}
          </div>
        </div>

        <div className="row">
          <div className="col s4">
            <b>Call time</b>
          </div>
          <div className="col s8">
            {`${moment(game.start).subtract(1, 'hours').format('hh:mm a')}`}
          </div>
        </div>

        {game.complete &&
          <div className="row">
            <div className="col s12">
              <b>This game is no longer accepting applications.</b>
            </div>
          </div>
        }


        {game.is_authenticated?
        (<div>
          {(game.has_applied && !game.complete)?(
            <div className="row">
              <div className="col s12 m6">
                <a href="" onClick={this.withdrawApplication} className="center waves-effect waves-light btn blue-grey darken-4 col s12">withdraw application</a>
              </div>
            </div>
          ):null}


          {(game.can_apply &&
          <div className="row">
            <div className="col s12 m6">
              <Link to={`/apply/${game.id}`} className="center waves-effect waves-light btn blue-grey darken-4 col s12">apply</Link>
            </div>
          </div>
          )}

          {(game.can_schedule &&
            <div className="row">
              <div className="col s12 m6">
                <Link to={`/games/${game.id}/schedule`} className="center waves-effect waves-light btn blue-grey darken-4 col s12">{game.complete?'view rosters':'schedule event'}</Link>
              </div>
            </div>
          )}

          {((game.can_schedule && !game.complete) &&
            <div className="row">
              <div className="col s12 m6">
                <Link to={`/games/${game.id}/edit`} className="col s12 center waves-effect waves-light btn blue-grey darken-4">Edit Event Information</Link>
              </div>
            </div>
          )}
        </div>)
        :
        !game.complete?(
          <div className="row">
            <div className="col s12 m6">
              <a href="/auth/login/facebook" className=" blue-grey darken-4 center waves-effect waves-light btn " >log in to apply</a>
              <div className="row">
                We use Facebook for logins so you don't have to remember another
                username/password. <a href={`/apply/${game.id}/luser`}>I'd rather not use Facebook</a>
              </div>
            </div>
          </div>
        ):null}


      </div>
    )
  }
}
