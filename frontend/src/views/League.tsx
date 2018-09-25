import * as React from "react";

import { EventList } from '../components/EventList';
import Navbar from "../components/Navbar";
import { BaseURL } from '../config';


export default class League extends EventList {
    protected endpoint = `${BaseURL}/api/league_schedule`;

    public getNavbar() {
      return (
          <Navbar user={this.props.user} button={{
            icon: "add_circle_outline",
            text: "Add Event",
            to: "/games/new"
          }} />
      );
    }
}
