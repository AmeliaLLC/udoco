import { EventList } from '../components/EventList';
import { BaseURL } from '../config';


export default class Schedule extends EventList {
    protected endpoint = `${BaseURL}/api/schedule`;
}
