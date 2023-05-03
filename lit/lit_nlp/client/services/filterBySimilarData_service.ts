import {action, computed, observable, reaction} from "mobx";

import {formatForDisplay, IndexedInput, ModelInfoMap, Spec} from '../lib/types';

import {LitService} from "./lit_service";
import {AppState} from "./state_service";

// HJ notes: stop using this service. Now deprecated
export class FilterBySimilarDataService extends LitService {

  @observable
  private selectedIndices = new Set<number>()

  @observable
  private commonTransforms = new Set<number>();

  @observable
  private transformsToData = new Map<number, Array<string>>();



  constructor(private readonly appState: AppState) {
    super()
  }

  @computed
  get commonTransformTypes() {
    console.log("commonTransformTypes");
    return new Set(this.commonTransforms);
  }

  @computed
  get dataSliceOfTransformType() {
    return this.transformsToData;
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

  @action
  addCommonTransforms(transformIndexes: Array<number>) {
    var transformIndexToType = {
      0: 'transform 0',
      1: 'transform 1',
      2: 'transform 2',
      3: 'transform 3',
      4: 'transform 4',
      5: 'transform 5',
    }

    console.log('add common transforms');
    var that = this;
    transformIndexes.forEach(function(transformIndex) {
      that.commonTransforms.add(transformIndex);
      console.log('common transforms is now ' + that.commonTransforms);
    });
  }

  @action
  initializeTransformsToDataIfNotExist(data : IndexedInput[]) {


    if (this.transformsToData.size) return;

    var that = this;
    // var transformsToData = new Map<number, Array<string>>();
    data.forEach(function (item) {
      // console.log('[initializeTransformsToDataIfNotExist]');
      // console.log(item.data['transforms'].substr(1, item.data['transforms'].length -1));
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
            that.transformsToData.set(element, new Array<string>());  
          } 

          // console.log('[initializeTransformsToDataIfNotExist] adding ' + element + "  <- " + item.id);
          // console.log(item);
          that.transformsToData.get(element).push(item.data['sentence']) ;
        });
    });

    // this.transformsToData = transformsToData;
  }


}