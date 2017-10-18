import { PropTypes } from 'prop-types';
import React, { Component } from 'react';


class DateSeparator extends Component {
  static propTypes = {
    date: (props, propName, componentName) => {
      const prop = props[propName];
      if (typeof(prop) !== 'object' || prop.getDate === undefined) {
          debugger;
        return new Error(
          'Invalid prop `' + propName + '` supplied to' +
          ' `' + componentName + '`. Validation failed.'
        );
      }
    }
  }
  render() {
    return (
      <li className="blue-grey lighten-4">{`${this.props.date}`}</li>
    );
  }
}


class Event extends Component {
  static propTypes = {
    title: PropTypes.string.isRequired,
    address: PropTypes.string.isRequired,
    eventId: PropTypes.number.isRequired,
    callTime: PropTypes.string.isRequired,
    league: PropTypes.string.isRequired
  }

  render() {
    return (
      <li className="collection-item">
        <div className="collapsible-header">
          {this.props.league} Presents - {this.props.title}
        </div>
        <div className="collapsible-body">
          <div className="row">{this.props.address}</div>
          <div className="row">Call time: {this.props.callTime}</div>
          <div className="row">
            <a href={`/apply/${this.props.eventId}`} className="center waves-effect waves-light btn">apply</a>
          </div>
        </div>
      </li>
    );
  }
}


class EventList extends Component {
  constructor(props) {
    super(props);
    this.state = {events: []};
  }

  componentWillMount() {
    const self = this;
    fetch('/api/events')
      .then((response) => (response.json()))
      .then((data) => {
        self.setState({events: data.results});
      });
  }

  render() {
    if (this.state.events.length > 0) {
      return (
      <ul className="collapsible" data-collapsible="expandable">
        <DateSeparator date={new Date()}/>
        <Event league="RMRG" title="Shitshowdown" address="Everywhere USA"
               eventId={83} callTime="5pm"/>
      </ul>
      );
    } else {
      return (
        <div>There are no events currently scheduled.</div>
      );
    }
  }
}

export { EventList };
