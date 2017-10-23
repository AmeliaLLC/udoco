import {createStore, applyMiddleware} from 'redux';
import thunk from 'redux-thunk';
import reducer from './reducers/index.js'
import logger from 'redux-logger';
import initialState from './initialState.js';

const middelware = [logger, thunk];

const store = createStore(reducer, initialState, applyMiddleware(...middelware));

export default store;
