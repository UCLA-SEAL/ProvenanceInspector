import {action, computed, observable, reaction} from "mobx";

import {LitService} from "./lit_service";
import {AppState} from "./state_service";

// HJ notes: stop using this service. Now deprecated
export class FilterBySimilarDataService extends LitService {

  @observable
  private selectedIndices = new Set<number>()


  constructor(private readonly appState: AppState) {
    super()
  }

  get markedIndices(): Set<number> {
    // return new Set(this.selectedIndices)
    return new Set();
  }

  @action
  selectDatapoint(index: number) {
    // this.selectedIndices.add(index)
  }

  @action
  unselectDatapoint(index: number) {
    // this.selectedIndices.delete(index)
  }

}