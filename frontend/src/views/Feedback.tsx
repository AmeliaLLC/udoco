import * as Materialize from "materialize-css";
import * as React from "react";
import { Redirect } from 'react-router-dom';

import Navbar from "../components/Navbar";
import { BaseURL } from '../config';
import { getCSRFToken } from '../util';


interface IFeedbackProps {
    user?: object;
}
interface IFeedbackState {
    feedback: string;
    redirect: boolean;
}


export default class Feedback extends React.Component <IFeedbackProps, IFeedbackState> {

    constructor(props: IFeedbackProps) {
        super(props);

        this.state = {
            feedback: '',
            redirect: false,
        };
    }

    public submitFeedback() {
        const url = `${BaseURL}/api/feedback`;
        const { feedback } = this.state;
        fetch(url, {
          body: JSON.stringify({message: feedback}),
          credentials: 'include',
          headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          method: "POST"
        })
        .then((response) => {
          if (response.status === 200) {
            Materialize.toast({
                displayLength: 1500,
                html: 'Thank you for your feedback.'
            });
            this.setState({redirect: true});
          } else {
            Materialize.toast({
                displayLength: 1500,
                html: 'Something went wrong. Please try again.'
            });
          }
        })
    }

    public render() {
        const self = this;
        return (
      <div>
        <Navbar user={this.props.user}/>

        <div className="container">
          <div className="row">
            <label htmlFor="feedback">Add Feedback</label>
          </div>

          <div className="row">
            <textarea id="feedback" className="materialize-textarea col s12 m6" onChange={
                data => {
                    if (data.target.value !== self.state.feedback) {
                        self.setState({feedback: data.target.value});
                    }
                }
            } />
          </div>

          <div className="row">
            <button className="waves-effect waves-light btn blue-grey darken-4 col s12 m6" onClick={this.submitFeedback.bind(this)}>submit feedback</button>
          </div>
        </div>
        {this.state.redirect && (<Redirect to="/"/>)}
      </div>
        );
    }
}
