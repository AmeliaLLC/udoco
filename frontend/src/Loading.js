import React from 'react';

export default class LoadingText extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      periods: 0
    }
    this.interval = setInterval(this.incrementor, 200);
  }
  incrementor= ()=> {
    if(this.state.periods === 3){
      this.setState({periods: 0});
    }else{
      this.setState({periods: this.state.periods + 1});
    }
  }
  render(){
    return (
      <h6 className="">{this.props.text}{'.'.repeat(this.state.periods)}</h6>
    )
  }
}
