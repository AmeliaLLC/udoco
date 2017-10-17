/* global jQuery*/
import { PropTypes } from 'prop-types';
import React, { Component } from 'react';

class Preference extends Component {
  render() {
    return (
      <div className="row">
        <div className="input-field col s6">
          <select name="preference[]">
            <option value="" disabled selected>Choose your option</option>
            <option value="1">Head ref</option>
            <option value="1">Inside pack ref</option>
            <option value="1">Jam ref</option>
            <option value="1">Outside pack ref</option>
          </select>
          <label>Preference</label>
        </div>
      </div>
    );
  }
}

class Apply extends Component {
  static propTypes = {
    title: PropTypes.string
  }
  static defaultProps = {
    title: "Shitshowdown"
  }
  componentDidMount() {
    jQuery('select').material_select();
  }
  render() {
    return (
      <div className="row">
        <form className="col s12">
          <h5>Apply to {this.props.title}</h5>
          <Preference />
          <div className="row">
            <div className="input-field col s12">
              <a className="center waves-effect waves-light btn">apply</a>
            </div>
          </div>
        </form>
      </div>
    );
  }
}
export default Apply;
