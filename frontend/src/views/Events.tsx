import { EventList } from '../components/EventList';
import { BaseURL } from '../config';


export default class Events extends EventList {
    protected endpoint = `${BaseURL}/api/games`;
}
