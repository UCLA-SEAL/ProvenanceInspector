import {action, computed, observable, reaction} from "mobx";

import {LitService} from "./lit_service";
import {AppState} from "./state_service";

export class QualityMarkService extends LitService {

  @observable
  private highQualityIndicesSet = new Set<number>()

  @observable
  private lowQualityIndicesSet = new Set<number>()

  constructor(private readonly appState: AppState) {
    super()
  }

  @computed
  get highQualityIndices(): Set<number> {
    return new Set(this.highQualityIndicesSet)
  }

  @computed
  get lowQualityIndices(): Set<number> {
    return new Set(this.lowQualityIndicesSet)
  }

  @action
  markHighQuality(index: number) {
    this.highQualityIndicesSet.add(index)
    this.unmarkLowQuality(index)
  }

  @action
  unmarkHighQuality(index: number) {
    this.highQualityIndicesSet.delete(index)
  }

  @action
  markLowQuality(index: number) {
    this.lowQualityIndicesSet.add(index)
    this.unmarkHighQuality(index)
  }

  @action
  unmarkLowQuality(index: number) {
    this.lowQualityIndicesSet.delete(index)
  }

}