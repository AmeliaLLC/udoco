
import React from 'react';


export default class Roster extends React.Component {

  updateRoster = ()=>{
    for(let ref in this.refs){
      if(this.refs[ref].value !== this.props.roster[ref]){
        let id = +this.refs[ref].value;
        let addedApplicant = this.props.applications.find((applicant)=>(applicant.id === id));
        if(!addedApplicant.hasOwnProperty('league_affiliation')){
          id = -id;
        }
        this.props.updateRoster(this.props.index, ref, id);
      }
    }
  }

  spotFilled = (spot)=>{
    let filledApplicantId = this.props.roster[spot];
    if(!filledApplicantId){
      return null;
    }
    let relevantUser = this.props.applications.find(user=>user.id===Math.abs(filledApplicantId));
    if (relevantUser === undefined) {
        console.err(`No relevant user found with id: ${filledApplicantId} and applications: ${this.props.applications}`);
        return null;
    }
    let name = relevantUser.display_name || relevantUser.derby_name;
    return name;
  }

  render(){
    var options = this.props.applications.map((application)=>(
      <option value={application.id}>{application.display_name || application.derby_name}</option>
    ));
    options.unshift((
      <option value="" disabled selected>Select Applicant</option>
    ));
    return (
      <div id={`roster${this.props.index}`}>
        <h1>{`ROSTER ${this.props.index+1}`}</h1>
        <div className="row">
          <div className="input-field col s12 m6">
          <form onChange={this.updateRoster}>

            <h6 className="center">Head Ref</h6>
            {this.spotFilled('hr')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('hr')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'hr')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
              this.props.completeEvent?(
                <p className="center bold">Unassigned</p>
              ):(
                <select id="Head Ref" ref="hr" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Alternate</h6>
            {this.spotFilled('alt')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('alt')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'alt')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
              this.props.completeEvent?
              (<p className="center bold">Unassigned</p>)
              :
              (
                <select id="Head Ref" ref="alt" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Head NSO</h6>
            {this.spotFilled('hnso')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('hnso')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'hnso')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="hnso" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Inside Pack Ref</h6>
            {this.spotFilled('ipr')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('ipr')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'ipr')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="ipr" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Wrangler</h6>
            {this.spotFilled('pw')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pw')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pw')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pw" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Inside Whiteboard</h6>
            {this.spotFilled('iwb')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('iwb')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'iwb')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="iwb" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Jam Timer</h6>
            {this.spotFilled('jt')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('jt')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'jt')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="jt" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Scoreboard Operator</h6>
            {this.spotFilled('so')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('so')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'so')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="so" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Box Manager</h6>
            {this.spotFilled('pbm')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pbm')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pbm')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pbm" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Non-Skating Official Alternate</h6>
            {this.spotFilled('nsoalt')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('nsoalt')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'nsoalt')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="nsoalt" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Period Timer</h6>
            {this.spotFilled('ptimer')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('ptimer')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'ptimer')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="ptimer" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Lineup Tracker</h6>
            {this.spotFilled('lt1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('lt1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'lt1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="lt1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Lineup Tracker</h6>
            {this.spotFilled('lt2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('lt2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'lt2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="lt2" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Box Timer</h6>
            {this.spotFilled('pbt1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pbt1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pbt1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pbt1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Box Timer</h6>
            {this.spotFilled('pbt2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pbt2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pbt2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pbt2" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Score Keeper</h6>
            {this.spotFilled('sk1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('sk1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'sk1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="sk1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Score Keeper</h6>
            {this.spotFilled('sk2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('sk2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'sk2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="sk2" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Tracker</h6>
            {this.spotFilled('pt1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pt1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pt1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pt1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Penalty Tracker</h6>
            {this.spotFilled('pt2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('pt2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'pt2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="pt2" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Outside Pack Ref</h6>
            {this.spotFilled('opr1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('opr1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'opr1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="opr1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Outside Pack Ref</h6>
            {this.spotFilled('opr2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('opr2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'opr2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="opr2" className=" center browser-default">
                  {options}
                </select>
              )
            }

            <h6 className="center">Outside Pack Ref</h6>
            {this.spotFilled('opr3')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('opr3')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'opr3')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="opr3" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Jam Ref</h6>
            {this.spotFilled('jr1')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('jr1')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'jr1')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
            this.props.completeEvent?
            (<p className="center bold">Unassigned</p>)
            :
              (
                <select id="Head Ref" ref="jr1" className=" center browser-default">
                  {options}
                </select>
              )
            }



            <h6 className="center">Jam Ref</h6>
            {this.spotFilled('jr2')!==null?
              (
                <div>
                  <h6 className="center bold">{this.spotFilled('jr2')}</h6>
                  <p className="center"><a  onClick={()=>{this.props.removePosition(this.props.index,'jr2')}} hidden={this.props.completeEvent}>reassign</a></p>
                </div>
              )
            :
              this.props.completeEvent?(
                <p className="center bold">Unassigned</p>
              ):(
                <select id="Head Ref" ref="jr2" className=" center browser-default">
                  {options}
                </select>
              )
            }









            </form>
          </div>
        </div>
        <div className="rosterController row" hidden={this.props.completeEvent}>

          <button onClick={()=>{this.props.saveEvent(this.props.index)}} className="waves-effect waves-light btn grey lighten-1 col s6 m3">
            save roster
          </button>

          <button className="waves-effect waves-light btn grey lighten-1 col s6 m3" onClick={()=>{this.props.deleteEvent(this.props.index)}}>
            delete roster
          </button>

        </div>
      </div>
    )
  }
}
