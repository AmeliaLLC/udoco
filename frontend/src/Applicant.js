import React from 'react';

export default class Applicant extends React.Component{
  constructor(props){
    super(props);
    let classes = [];
    for (let i = 0; i < props.preferences.length; i++){
      classes.push(null);
    }
    this.state = {classes};
  }
  render(){
    return (
      <div className="row">
        <div className="col s12">
          <ul className="collapsible">
            <li>
              <div className="collapsible-header">{this.props.name}</div>
              <div className="collapsible-body">
                <h6><b>Preferred Positions</b></h6>
                {this.props.preferences.map((preference,index)=>(
                  <div onClick={()=>{this.select(index)}} className={"chip "+this.state.classes[index]}>
                    {preference}
                  </div>))
                }
                <hr/>
                <h6><b>Notes</b></h6>
                <p>{`"${this.props.notes}"`}</p>
                <br/>
                <a hidden={true}>VIEW ACCOUNT</a>
              </div>
            </li>
          </ul>

        </div>
      </div>
    )
  }
}
