/* global jQuery */
import React from 'react';
import LoadingText from './Loading.js';
import Applicant from './Applicant.js'
import { Navbar } from './Navigation.js';
import { BaseURL } from './config.js';
import { confirmAlert } from 'react-confirm-alert';
import { getCSRFToken } from './utils.js';
import RosterComponent from './ROster.js';

function Roster(){
  this['hr'] = "";
  this['alt'] = "";
  this['hnso'] = "";
  this['ipr'] = "";
  this['pw'] = "";
  this['iwb'] = "";
  this['jt'] = "";
  this['so'] = "";
  this['pbm'] = "";
  this['nsoalt'] = "";
  this['ptimer'] = "";
  this['lt1'] = "";
  this['lt2'] = "";
  this['pbt1'] = "";
  this['pbt2'] = "";
  this['sk1'] = "";
  this['sk2'] = "";
  this['pt1'] = "";
  this['pt2'] = "";
  this['opr1'] = "";
  this['opr2'] = "";
  this['opr3'] = "";
  this['jr1'] = "";
  this['jr2'] = "";
}

export default class ScheduleEvent extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      event: {},
      applications: [],
      waiting: true,
      rosters: []
    };
  }
  componentWillMount(){
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}`,{
      method: 'GET',
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then(response=>response.json())
    .then((eventInfo)=>{
      if(!eventInfo.can_schedule){
        window.location = '/';
      }
      this.setState({event: eventInfo});
    });


    fetch(`${BaseURL}/api/games/${this.props.match.params.id}/applications`,{
      method: 'GET',
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    }).then((response)=>{
      return response.json();
    })
    .then((applications)=>{
      this.setState({applications},()=>{
        fetch(`${BaseURL}/api/games/${this.props.match.params.id}/lapplications`,{
          method: 'GET',
          credentials: 'include',
          headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-type': 'application/json'
          }
        })
        .then(response => response.json())
        .then((lapplications)=>{
          let copy = this.state.applications.splice('');
          copy = copy.concat(lapplications);
          this.setState({applications: copy},()=>{
            fetch(`${BaseURL}/api/games/${this.props.match.params.id}/rosters`,{
              method: 'GET',
              credentials: 'include',
              headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-type': 'application/json'
              }
            })
            .then((response)=>(response.json()))
            .then((rosters)=>{
              console.log('received rosters:\n', rosters);
              rosters.forEach((roster)=>{
                for(let position in roster){
                  if(roster[position]===null){
                    roster[position] = "";
                  }
                }
              });
              this.setState({rosters, waiting: false});
            });
          });
        });
      });
    });
  }

  componentDidUpdate(){
    jQuery('.collapsible').collapsible();
    jQuery('ul.tabs').tabs();
  }


  createRoster = () =>{
    let newRoster = new Roster();
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}/rosters/`,{
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify(newRoster),
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Yo-Momma': 'DAAAAANG!',
        'Content-type': 'application/json'
      }
    })
    .then((response)=>{
      return response.json()
    })
    .then((createdRoster)=>{
      for (let position in createdRoster){
        if(createdRoster[position]===null){
          createdRoster[position] = "";
        }
      }
      let copy = this.state.rosters.slice('');
      copy.push(createdRoster);
      this.setState({rosters: copy});
    })
  }

  updateRoster=(index, role, userId)=>{
    let copy = this.state.rosters.slice('');
    copy[index][role] = userId;
    this.setState({rosters: copy});
  }
  removePosition = (index, position)=>{
    let copy = this.state.rosters.slice('');
    copy[index][position] = null;
    this.setState({rosters: copy});
  }
  saveEvent = (index) =>{
    let savedRoster = Object.assign({},this.state.rosters[index]);
    for (let position in savedRoster){
      if(savedRoster[position] === ""){
        savedRoster[position] = null;
      }
    }
    let id = savedRoster.id;
    delete savedRoster.id;
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}/rosters/${id}/`,{
      method: 'PUT',
      credentials: 'include',
      body: JSON.stringify(savedRoster),
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then((response)=>{
      return response.json()
    })
    .then((updateRoster)=>{
      console.log('saved roster:\n',updateRoster);
    });
  }
  submitEvent = (index) => {
    confirmAlert({
      title: 'Finalize Event?',
      message: 'This will make all rosters uneditable and notify all applicants. All unsaved changes will not be applied. Are you sure?',
      confirmLabel: 'Yes',
      cancelLabel: 'Nevermind',
      onConfirm: ()=>{
        fetch(`${BaseURL}/api/games/${this.props.match.params.id}`,{
          method: 'PATCH',
          credentials: 'include',
          body: JSON.stringify({complete: true}),
          headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-type': 'application/json'
          }
        })
        .then(response=>response.json())
        .then((response)=>{
          window.location = '/';
        });
      }
    });
  }
  deleteEvent = (index) => {
    let deletedEvent = this.state.rosters[index];
    fetch(`${BaseURL}/api/games/${this.props.match.params.id}/rosters/${deletedEvent.id}/`,{
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-type': 'application/json'
      }
    })
    .then(()=>{
      let copy = this.state.rosters.slice();
      copy.splice(index,1);
      this.setState({rosters: copy});
    });
  }

  render(){
    return (
      <div>
        <Navbar user={this.props.user} button={this.state.event.complete?null:{
          text: "New Roster",
          action: this.createRoster,
          icon: "playlist_add"
        }}/>

        {this.state.waiting?
          (
          <LoadingText text="Gathering Applications"/>
          )
          :
          <div>
            <ul className="collapsible" data-collapsible="accordion">
              <li>
                <div className="collapsible-header">View Applicants</div>
                <div className="collapsible-body">
                {(this.state.applications.length === 0 &&
                  <p>There are no Applicants for this event.</p>
                )}
                {this.state.applications.map((application)=>(<Applicant name={application.display_name || application.derby_name} preferences={application.preferences} addToRoster={this.addToRoster}/>))}
                </div>
              </li>
            </ul>
            {this.state.rosters.length !==0?(
              <div className="card">
                <div className="card-content">
                  You have {this.state.rosters.length} rosters to manage for this event.
                </div>
                <div className="card-tabs">
                  <ul className="tabs">
                    {this.state.rosters.map((roster,index)=>(
                      <li className="tab"><a href={`#roster${index}`}>{`Roster #${index+1}`}</a></li>
                    ))}
                  </ul>
                </div>
                <div className="card-content grey lighten-4">
                  {this.state.rosters.map((roster, index)=>(
                    <RosterComponent roster={roster} index={index} applications={this.state.applications} updateRoster={this.updateRoster} removePosition={this.removePosition}
                    saveEvent={this.saveEvent}
                    deleteEvent={this.deleteEvent}
                    completeEvent={this.state.event.complete}
                    />
                  ))}
                </div>
                <div className="row" hidden={this.state.event.complete}>
                  <button onClick={this.submitEvent} className="waves-effect waves-light btn grey lighten-1 col s12">
                    finalize event
                  </button>
                </div>
              </div>
            )
            :
            (
              <p>You have no available rosters!</p>
            )
          }
          </div>
        }


      </div>
    )
  }
}
