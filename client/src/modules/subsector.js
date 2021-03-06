import * as api from '../api';
import { createAction } from './utils';
import { clearSearch } from './search';

const WORLD_SELECTED = 'traveler-starmap/subsector/WORLD_SELECTED';
const SELECT_ALL = 'traveler-starmap/subsector/SELECT_ALL';
const NEW_SUBSECTOR_REQUEST = 'traveler-starmap/subsector/NEW_SUBSECTOR_REQUEST';
const NEW_SUBSECTOR_SUCCESS = 'traveler-starmap/subsector/NEW_SUBSECTOR_SUCCESS';
const NEW_SUBSECTOR_FAILURE = 'traveler-starmap/subsector/NEW_SUBSECTOR_FAILURE';

export const selectWorld = world => createAction(WORLD_SELECTED, world);
export const selectAll = () => createAction(SELECT_ALL);

const fetchSubsector = (fn, world) => {
  return dispatch => {
    dispatch(createAction(NEW_SUBSECTOR_REQUEST));
    fn()
    .then(subsector => {
      dispatch(createAction(NEW_SUBSECTOR_SUCCESS, { subsector, selected: world }));
    }, err => {
      dispatch(NEW_SUBSECTOR_FAILURE, err);
    });
  };
};

export function getRandomSubsector() {
  return fetchSubsector(() => api.get('random/'));
}

export function newSubsector() {
  return fetchSubsector(() => api.post(''));
}

export function jumpTo(searchResult) {
  return dispatch => {
    dispatch(clearSearch());
    const url = searchResult.subsector.id + '/';
    dispatch(fetchSubsector(() => api.get(url), searchResult.world));
  };
}

const initialState = {
  subsector: null,
  selected: null,
};

export default function (state = initialState, action) {
  switch (action.type) {
    case SELECT_ALL:
      return { ...state, selected: null };
    case WORLD_SELECTED:
      return { ...state, selected: action.payload };
    case NEW_SUBSECTOR_REQUEST:
      return { ...state, subsector: null, selected: null };
    case NEW_SUBSECTOR_SUCCESS:
      return { ...state, ...action.payload };
    default:
      return state;
  }
}
