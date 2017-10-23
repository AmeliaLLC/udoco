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
  select=(index)=>{
    // let copy = this.state.classes.slice('');
    // if(!copy[index]){
    //   copy[index] = " blue lighten-2";
    // }else{
    //   copy[index] = null;
    // }
    //
    // this.setState({classes:copy});
    // let rosterAddition = {
    //   role: this.props.preferences[index],
    //   name: this.props.name
    // };
    // this.props.addToRoster(rosterAddition);
  }
  render(){
    return (
      <div className="row">
        <div className="col s12">
          <ul className="collapsible">
            <li>
            <div className="collapsible-header">{this.props.name}</div>
            <div className="collapsible-body">
              {this.props.preferences.map((preference,index)=>(
                <div onClick={()=>{this.select(index)}} className={"chip "+this.state.classes[index]}>
                  {preference}
                </div>))
              }
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
