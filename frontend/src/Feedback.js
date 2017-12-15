/* global Materialize */
import React from 'react';
import {Redirect} from 'react-router-dom';
import {Navbar} from './Navigation.js';
import { getCSRFToken } from './utils.js';
import { BaseURL } from './config.js';

export default class Feedback extends React.Component{
  constructor(props){
    super(props);
    this.state={
      feedback: '',
      redirect: false
    };
  }
  updateFeedback = ()=>{
    this.setState({feedback: this.refs.feedback.value});
  }
  submitFeedback = ()=>{
    fetch(`${BaseURL}/api/feedback`,{
      method: "POST",
      credentials: 'include',
      body: JSON.stringify({message: this.state.feedback}),
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then((response) => {
      if(response.status === 200){
        Materialize.toast('Thank you for your feedback.', 1500);
        this.setState({redirect: true});
      }else{
        Materialize.toast('Something went wrong. Please try again.', 1500);
      }
    })

  }
  render(){
    return(
      <div>
        <Navbar user={this.props.user}/>

        <div className="container">
          <div className="row">
            <label HTMLfor="feedback">Add Feedback</label>
          </div>

          <div className="row">
            <textarea id="feedback" className="materialize-textarea col s12 m6" onChange={this.updateFeedback} ref="feedback"></textarea>
          </div>

          <div className="row">
            <button className="waves-effect waves-light btn blue-grey darken-4 col s12 m6" onClick={this.submitFeedback}>submit feedback</button>
          </div>
        </div>
        {this.state.redirect && (<Redirect to="/"/>)}
      </div>
    )
  }
}
