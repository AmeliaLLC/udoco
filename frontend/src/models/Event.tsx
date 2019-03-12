import { IRosterModel } from './Roster';

interface IEventModel {
    league: string;
    title: string;
    id: number;
    location: string;
    start: string;
    complete: string;
    has_applied: boolean;
    can_apply: boolean;
    can_schedule: boolean;
    is_authenticated: boolean;
    is_rostered: boolean;
    rostered_as: string[];

    rosters: IRosterModel[];
}

export { IEventModel };
