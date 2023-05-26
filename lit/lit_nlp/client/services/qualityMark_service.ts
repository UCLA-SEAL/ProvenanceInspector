import {action, computed, observable, reaction} from "mobx";

import {LitService} from "./lit_service";
import {AppState} from "./state_service";

export class QualityMarkService extends LitService {

  @observable
  private highQualityIndicesSet = new Set<number>()

  @observable
  private lowQualityIndicesSet = new Set<number>();

  @observable
  private highQualityTransformsSet = new Set<number>();

  @observable
  private lowQualityTransformsSet = new Set<number>();

  @observable
  private highQualityFeaturesSet = new Set<number>();

  @observable
  private lowQualityFeaturesSet = new Set<number>();

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

  @computed
  get highQualityTransforms(): Set<number> {
    return new Set(this.highQualityTransformsSet)
  }

  @computed
  get highQualityFeatures(): Set<number> {
    return new Set(this.highQualityFeaturesSet)
  }

  @computed
  get lowQualityTransforms(): Set<number> {
    return new Set(this.lowQualityTransformsSet)
  }

  @computed
  get lowQualityFeatures(): Set<number> {
    return new Set(this.lowQualityFeaturesSet)
  }

  @action
  markHighQuality(index: number) {
    this.highQualityIndicesSet.add(index)
    this.markLowQuality(index)
  }

  @action
  unmarkHighQuality(index: number) {
    this.highQualityIndicesSet.delete(index)
  }

  @action
  markLowQuality(index: number) {
    this.lowQualityIndicesSet.add(index)
  }

  @action
  unmarkLowQuality(index: number) {
    this.lowQualityIndicesSet.delete(index)
  }

  @action
  markHighQualityTransforms(transform: number) {
    this.highQualityTransformsSet.add(transform);
  }

  @action
  markLowQualityTransforms(transform: number) {
    this.lowQualityTransformsSet.add(transform);
  }

  @action
  unmarkHighQualityTransforms(transform: number) {
    this.highQualityTransformsSet.delete(transform);
  }

  @action
  unmarkLowQualityTransforms(transform: number) {
    this.lowQualityTransformsSet.delete(transform);
  }

  @action
  markHighQualityFeatures(feature: number) {
    this.highQualityFeaturesSet.add(feature);
  }

  @action
  markLowQualityFeatures(feature: number) {
    this.lowQualityFeaturesSet.add(feature);
  }

  @action
  unmarkHighQualityFeatures(feature: number) {
    this.highQualityFeaturesSet.delete(feature);
  }

  @action
  unmarkLowQualityFeatures(feature: number) {
    this.lowQualityFeaturesSet.delete(feature);
  }

  @action
  clearAllData() {
    this.highQualityFeaturesSet.clear();
    this.lowQualityFeaturesSet.clear();
    this.highQualityTransformsSet.clear();
    this.lowQualityTransformsSet.clear();
    this.highQualityIndicesSet.clear();
    this.lowQualityIndicesSet.clear();
  }

}