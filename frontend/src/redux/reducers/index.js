import {combineReducers} from 'redux';
import initialState from '../initialState.js';
// import {sameDoma}

export default combineReducers({});
export default (state = initialState, action) =>{

  switch (action.type){
    default:
      return state;
  }
}
