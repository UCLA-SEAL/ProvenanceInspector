import {action, computed, observable, reaction} from "mobx";

import {formatForDisplay, IndexedInput, ModelInfoMap, Spec} from '../lib/types';

import {LitService} from "./lit_service";
import {AppState} from "./state_service";

export class FilterBySimilarDataService extends LitService {


  @observable
  private selectedIndices = new Set<number>()

  @observable
  private commonTransforms = new Set<number>();

  @observable
  private commonFeatures = new Set<number>();

  @observable
  private transformsToData = new Map<number, Array<object>>();

  @observable
  private featuresToData = new Map<number, Array<object>>();

  constructor(private readonly appState: AppState) {
    super()
  }

  @computed
  get commonTransformTypes() {
    return new Set(this.commonTransforms);
  }

  @computed
  get commonFeatureTypes() {
    return new Set(this.commonFeatures);
  }

  @computed
  get dataSliceOfTransformType() {
    return this.transformsToData;
  }

  @computed
  get dataSliceOfFeatureType() {
    return this.featuresToData;
  }

  @computed 
  get datapointsWithTransforms() {
    return this.transformsToData;
  }

  @computed 
  get datapointsWithFeatures() {
    return this.featuresToData;
  }

  get markedIndices(): Set<number> {
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

  @action
  setCommonTransforms(transformIndexes: Array<number>) {

    var that = this;
    that.commonTransforms.clear();
    transformIndexes.forEach(function(transformIndex) {
      that.commonTransforms.add(transformIndex);
      
    });
  }

  @action
  setCommonFeatures(featureIndexes: Array<number>) {
   
    var that = this;

    that.commonFeatures.clear();
    featureIndexes.forEach(function(featureIndex) {
      that.commonFeatures.add(featureIndex);

    });
  }

  @action
  initializeTransformsToDataIfNotExist(data : IndexedInput[]) {


    if (this.transformsToData.size) return;

    var that = this;
    // var transformsToData = new Map<number, Array<string>>();
    data.forEach(function (item) {
      
      item.data['transforms'].substr(1, item.data['transforms'].length -1).split(' ')
        .map(strElement => parseInt(strElement))
        .map((element, index) => {
          if (element === 1) {
            return index;
          }
        })
        .filter(element => element !== undefined)
        .forEach(function(element) { 
          if (!that.transformsToData.has(element)) {
            that.transformsToData.set(element, new Array());  
          } 

          that.transformsToData.get(element).push({
            'id': item.id,
            'idx': item.data['idx'],
            'text': item.data['diff'],
            "label": item.data['label']
          }) ;
        });
    });

    // this.transformsToData = transformsToData;
  }

  @action
  initializeFeaturesToDataIfNotExist(data : IndexedInput[]) {
    if (this.featuresToData.size) return;

    var that = this;
    
    data.forEach(function (item) {
      
      item.data['features'].substr(1, item.data['features'].length -1).split(' ')
        .map(strElement => parseInt(strElement))
        .map((element, index) => {
          if (element === 1) {
            return index;
          }
        })
        .filter(element => element !== undefined)
        .forEach(function(element) { 
          if (!that.featuresToData.has(element)) {
            that.featuresToData.set(element, new Array());  
          } 

          that.featuresToData.get(element).push({
            'id': item.id,
            'idx': item.data['idx'],
            'text': item.data['old_sentence'],
            "label": item.data['label']
          }) ;
        });
    });
  }

  clearAllData() {
    this.commonTransforms.clear();
    this.commonFeatures.clear();
    this.transformsToData.clear();
    this.featuresToData.clear();
  }


}