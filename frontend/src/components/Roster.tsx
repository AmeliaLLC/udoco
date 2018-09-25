import * as React from "react";
import * as ReactDOM from 'react-dom';

import { IRosterModel } from '../models/Roster';


interface IRosterPositionProps {
    title: string;
    indicator: string;
    value: number | null;

    options: JSX.Element[];
}


class RosterPosition extends React.Component<IRosterPositionProps, {}> {

    constructor(props: IRosterPositionProps) {
        super(props);
    }

    public render() {
        return (
            <div>
                <h6 className="center">{this.props.title}</h6>

                <select id={this.props.indicator} onChange={() => { return; }} value={this.props.value !== null ? this.props.value : ""} className=" center browser-default roster-position">
                    {this.props.options}
                </select>
            </div>
        );
    }

}

interface IRosterProps {
    roster: any;
    index: number;
    applications: any[];
    lapplications: any[];

    updateRoster: any;  // Function
    removePosition: any;  // Function
    saveRoster: any;  // Function
    deleteRoster: any;  // Function
}

export default class Roster extends React.Component<IRosterProps, {}> {

    constructor(props: IRosterProps) {
        super(props);
    }

    public render(): JSX.Element {
        return (
            <div id={"roster"+this.props.index} className="col s12">
                <h6>Roster {this.props.index+1}</h6>

                <div className="row">
                    <div className="input-field col s12 m6">
                        <form onChange={this.updateRoster.bind(this)}>
                            <RosterPosition title="Head ref" indicator="hr" options={this.getOptionsForRoster('hr')} value={this.props.roster.hr} />
                            <RosterPosition title="Inside pack ref" indicator="ipr" options={this.getOptionsForRoster('ipr')} value={this.props.roster.ipr} />
                            <RosterPosition title="Jam ref" indicator="jr1" options={this.getOptionsForRoster('jr1')} value={this.props.roster.jr1} />
                            <RosterPosition title="Jam ref" indicator="jr2" options={this.getOptionsForRoster('jr2')} value={this.props.roster.jr2} />
                            <RosterPosition title="Outside pack ref" indicator="opr1" options={this.getOptionsForRoster('opr1')} value={this.props.roster.opr1} />
                            <RosterPosition title="Outside pack ref" indicator="opr2" options={this.getOptionsForRoster('opr2')} value={this.props.roster.opr2} />
                            <RosterPosition title="Outside pack ref" indicator="opr3" options={this.getOptionsForRoster('opr3')} value={this.props.roster.opr3} />
                            <RosterPosition title="Alternate ref" indicator="alt" options={this.getOptionsForRoster('alt')} value={this.props.roster.alt} />

                            <RosterPosition title="Head NSO" indicator="hnso" options={this.getOptionsForRoster('hnso')} value={this.props.roster.hnso} />
                            <RosterPosition title="Jam Timer" indicator="jt" options={this.getOptionsForRoster('jt')} value={this.props.roster.jt} />
                            <RosterPosition title="Penalty/Lineup Tracker" indicator="pt1" options={this.getOptionsForRoster('pt1')} value={this.props.roster.pt1} />
                            <RosterPosition title="Penalty/Lineup Tracker" indicator="pt2" options={this.getOptionsForRoster('pt1')} value={this.props.roster.pt2} />
                            <RosterPosition title="Scoreboard Operator" indicator="so" options={this.getOptionsForRoster('so')} value={this.props.roster.so} />
                            <RosterPosition title="Scorekeeper" indicator="sk1" options={this.getOptionsForRoster('sk1')} value={this.props.roster.sk1} />
                            <RosterPosition title="Scorekeeper" indicator="sk2" options={this.getOptionsForRoster('sk2')} value={this.props.roster.sk2} />
                            <RosterPosition title="Penalty Box Manager" indicator="pbm" options={this.getOptionsForRoster('pbm')} value={this.props.roster.pbm} />
                            <RosterPosition title="Penalty Box Timer" indicator="pbt1" options={this.getOptionsForRoster('pbt1')} value={this.props.roster.pbt1} />
                            <RosterPosition title="Penalty Box Timer" indicator="pbt2" options={this.getOptionsForRoster('pbt2')} value={this.props.roster.pbt2} />
                            <RosterPosition title="Alt NSO" indicator="nsoalt" options={this.getOptionsForRoster('nsoalt')} value={this.props.roster.nsoalt} />
                        </form>
                    </div>
                </div>

                <div className="rosterController row">
                  <button onClick={()=>{this.props.saveRoster(this.props.index)}} className="waves-effect waves-light btn grey lighten-1 col s6 m3">
                    save roster
                  </button>

                  <button className="waves-effect waves-light btn grey lighten-1 col s6 m3" onClick={()=>{this.props.deleteRoster(this.props.index)}}>
                    delete roster
                  </button>
                </div>
            </div>
        );
    }

    private getOptionsForRoster(position: string): JSX.Element[] {
        const applications = this.props.applications.map((application, index) => (
            <option key={position + '-' + this.props.index + '-' + application.id} value={application.id}>{application.display_name || application.derby_name}</option>
        ));
        const options = applications.concat(this.props.lapplications.map((application, index) => (
            <option key={position + '-' + this.props.index + '-' + (0 - application.id)} value={0 - application.id}>{application.derby_name}</option>
        )));
        options.unshift((
              <option key="select" value="" disabled={true}>Select Applicant</option>
        ));
        return options;
    }

    private updateRoster(e: React.FormEvent<HTMLFormElement>) {
        const target = e.target as HTMLFormElement;

        const role = target.getAttribute('id');
        const value = Number(target.value);

        this.props.updateRoster(this.props.index, role, value)
    }

    private spotFilled(spot: string): number | null {
        const filledApplicantId = Number(this.props.roster[spot]);

        if (!filledApplicantId) {
            return null;
        }
        return filledApplicantId;
    }
}
