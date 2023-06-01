/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// tslint:disable:no-new-decorators
import { customElement, property } from 'lit/decorators'
import { html, svg } from 'lit'
import { action, computed, observable } from 'mobx'

import { LitModule } from '../core/lit_module'

import { IndexedInput } from '../lib/types'
import { getTextWidth, getTokOffsets, sumArray } from '../lib/utils'
import { ColumnHeader, TableData, TableEntry } from '../elements/table';
import {unsafeHTML} from 'lit-html/directives/unsafe-html.js';
import {PopupContainer} from '../elements/popup_container';

import * as papa from 'papaparse';

import { styles as sharedStyles } from '../lib/shared_styles.css'
import { styles } from './tx_transform_provenance_module.css'
import { getBrandColor } from '../lib/colors'
import { app } from '../core/app'
import { QualityMarkService } from '../services/qualityMark_service'
import { FilterBySimilarDataService } from '../services/filterBySimilarData_service'

@customElement('tx-transform-provenance-module')
export class TxTransformProvenanceModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles]
  }

  static override title = 'Transform Provenance'
  static override numCols = 2
  static override collapseByDefault = false
  static override duplicateForModelComparison = false

  private readonly qualityMarkService = app.getService(QualityMarkService);
  private readonly filterBySimilarDataService = app.getService(FilterBySimilarDataService);

  static override template = () => {
    return html`<tx-transform-provenance-module></tx-transform-provenance-module>`
  }

  @observable private isLoading = false
  @observable private commonTransforms;
  @observable private highQualityTransforms;


  @property({type: String}) downloadFilename: string = 'transform_provenance_enabled.csv';

  override firstUpdated() {
    this.reactImmediately(
      () => this.filterBySimilarDataService.commonTransformTypes,
      commonTransforms => this.updateTransforms(commonTransforms)
    )

    this.reactImmediately(
      () => this.qualityMarkService.highQualityTransforms,
      highQualityTransform => this.updateHighQTransforms(highQualityTransform)
    )
    
  }

  private transformNamesRaw(transformIndex : number) {
    var mapping = [
      "AddNeutralEmoji",
      "ChangeHypernym",
      "ChangeHyponym",
      "ChangeLocation",
      "ChangeName",
      "ChangeNumber",
      "ChangeSynonym",
      "ContractContractions",
      "ExpandContractions",
      "HomoglyphSwap",
      "InsertPunctuationMarks",
      "RandomCharDel",
      "RandomCharInsert",
      "RandomCharSubst",
      "RandomCharSwap",
      "RandomInsertion",
      "RandomSwap",
      "RandomSwapQwerty",
      "RemoveNeutralEmoji",
      "WordDeletion"]

      return mapping[transformIndex]
  }

  private transformNames(transformIndex : number) {
    var mapping = [
      "AddNeutralEmoji (adds a non-emotional emoji)",
      "ChangeHypernym (replace words with words of a broader meaning)",
      "ChangeHyponym (replace words with words of more specific meaning)",
      "ChangeLocation (change locations in the sentence)",
      "ChangeName (change names in the sentence)",
      "ChangeNumber (change numbers in the sentence)",
      "ChangeSynonym (replace words with other words with the same meaning)",
      "ContractContractions (contracts the contractions in the sentence)",
      "ExpandContractions (expands the contractions in the sentence)",
      "HomoglyphSwap (replaces words with visually similar words)",
      "InsertPunctuationMarks (Inserts random punctuation marks to random spots)",
      "RandomCharDel (remove a randomly selected character in the sentence)",
      "RandomCharInsert (inserts a randomly selected character in the sentence)",
      "RandomCharSubst (replace a randomly selected character in the sentence with another character)",
      "RandomCharSwap (swap random consecutive character in the sentence)",
      "RandomInsertion (inserts random words in the sentence)",
      "RandomSwap (replaces a randomly selected word in the sentence with another",
      "RandomSwapQwerty (substitues random characters with adjacent keys on a keyboard)",
      "RemoveNeutralEmoji (removes a non-emotional emoji)",
      "WordDeletion (removes words from the sentence)"]

      return mapping[transformIndex]
  }

  private numMatchingInstances(featureIndex : number) {
    var matchingDatapoints = this.filterBySimilarDataService.dataSliceOfTransformType.get(featureIndex);
    if (!matchingDatapoints) {
      return 0;
    }
    return matchingDatapoints.length;
  }

  private numSelectedInstances(featureIndex: number) {

    var matchingDatapoints = this.filterBySimilarDataService.dataSliceOfTransformType.get(featureIndex);
    if (!matchingDatapoints) {
      return 0;
    }

    console.log('matchingDatapoints');
    console.log(matchingDatapoints)
    console.log('this.selectionService.selectedIds');
    console.log(this.selectionService.selectedIds);
    return matchingDatapoints.filter(matchingDatapoint => {
      return this.selectionService.selectedIds.indexOf(matchingDatapoint['id']) > 0;
    }).length;
    
  }

  private numMatchingHighQInstances(featureIndex : number) {
    var matchingDatapoints = this.filterBySimilarDataService.dataSliceOfTransformType.get(featureIndex);
    if (!matchingDatapoints) {
      return 0;
    }
    return matchingDatapoints.filter(datapoint => {
      return this.qualityMarkService.highQualityIndices.has(datapoint['idx'])
    }).length;
  }

  private numMatchingLowQInstances(featureIndex : number) {
    var matchingDatapoints = this.filterBySimilarDataService.dataSliceOfTransformType.get(featureIndex);
    if (!matchingDatapoints) {
      return 0;
    }
    return matchingDatapoints.filter(datapoint => {
      return this.qualityMarkService.lowQualityIndices.has(datapoint['idx'])
    }).length;
  }


  private async onSelectEnable(commonTransform : number, isAlreadySelected: boolean) {
    // this.selectedInputData = selectedInputData.map(
    //   input => ({ idx: this.appState.getIndexById(input.id), ...input })
    // )
    // if (this.selectedInputData.length == 0) return
    // this.isLoading = true;

    // this.isLoading = false;
    // console.log('[onSelectEnable] ' + commonTransform);

    if (!isAlreadySelected) {
      this.qualityMarkService.markHighQualityTransforms(commonTransform);
      this.qualityMarkService.markLowQualityTransforms(commonTransform);

      // propagate label to all data instances with the common transform
      
      var matchingDatapoints = this.filterBySimilarDataService.datapointsWithTransforms.get(commonTransform);

      matchingDatapoints.forEach(matchingDatapoint => 
        this.qualityMarkService.markHighQuality(matchingDatapoint['idx'])
      )
        
      


    } else {
        this.qualityMarkService.unmarkHighQualityTransforms(commonTransform);

        // propagate label to all data instances with the common transform
    
        var matchingDatapoints = this.filterBySimilarDataService.datapointsWithTransforms.get(commonTransform);

        matchingDatapoints.forEach(matchingDatapoint => 
          this.qualityMarkService.unmarkHighQuality(matchingDatapoint['idx'])
        )
    }
    // if (this.highQualityTransforms == undefined) {
    //   this.highQualityTransforms = new Set();
    // }
    // this.highQualityTransforms.add(commonTransform);
  }


  private async onSelectInspected(commonTransform : number, isAlreadySelected: boolean) {
    if (!isAlreadySelected) {
      this.qualityMarkService.markLowQualityTransforms(commonTransform);

      // propagate label to all data instances with the common transform
      
      var matchingDatapoints = this.filterBySimilarDataService.datapointsWithTransforms.get(commonTransform);

      matchingDatapoints.forEach(matchingDatapoint => 
        this.qualityMarkService.markLowQuality(matchingDatapoint['idx'])
      )
    } else {
        this.qualityMarkService.unmarkLowQualityTransforms(commonTransform);

        // propagate label to all data instances with the common transform
    
        var matchingDatapoints = this.filterBySimilarDataService.datapointsWithTransforms.get(commonTransform);

        matchingDatapoints.forEach(matchingDatapoint => 
          this.qualityMarkService.unmarkLowQuality(matchingDatapoint['idx'])
        )
    }
  }

  private async updateTransforms(incomingTransforms){
    // console.log("[provenance] updateTransforms")
    // console.log(incomingTransforms);
    this.commonTransforms = new Set(incomingTransforms);
  }

  private async updateHighQTransforms(qualityTransforms){
    // console.log("[provenance] updateHighQTransforms")
    // console.log(qualityTransforms);
    this.highQualityTransforms = new Set(qualityTransforms);
  }



  override render() {
    // clang-format off
    if (this.isLoading) {
      return html`
        <div class="module-container">
          <p>
            Loading...
          </p>
        </div>
      `
    }

    const columns: ColumnHeader[] = ['Transform', 'Mark all as high quality', 'Mark all as inspected', 'Transformed texts'].map(
      field => ({
        name: field,
        centerAlign: true,
      })
    )

    const updateFilename = (e: Event) => {
      // tslint:disable-next-line:no-any
      this.downloadFilename = (e as any).target.value as string;
    };

    const getSelectedTransforms = () => {
      const selectedTransforms = [];
      for (const transform of this.highQualityTransforms) {
        selectedTransforms.push([this.transformNamesRaw(transform), "1"]);
      }
      return selectedTransforms;
    }

    const csvContent = function() {
      return papa.unparse(
        {fields: ['transform'], data: getSelectedTransforms()},
        {newline: '\r\n'});

    }

    const downloadCSV = () => {
      const content = csvContent();
      const blob = new Blob([content], {type: 'text/csv'});
      const a = window.document.createElement('a');
      a.href = window.URL.createObjectURL(blob);
      a.download = this.downloadFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      const controls: PopupContainer =
          this.shadowRoot!.querySelector('popup-container.download-popup')!;
      controls.expanded = false;
    };

    function onEnter(e: KeyboardEvent) {
      if (e.key === 'Enter') downloadCSV();
    }
      
    const rows = [];

    
    if (this.commonTransforms) {

      var dataSlices = this.filterBySimilarDataService.dataSliceOfTransformType;

      var that = this;
      this.commonTransforms.forEach(function(commonTransform) {

        const previewSliceData = dataSlices.get(commonTransform)
        .slice(0, 3);

        // wrap it in html
        const previewSlice = 
          '<div class="preview-slice-holder" style="width:100%">' + 
        previewSliceData.map( 
          (d, i) => {
            return `<div class="preview-slice" style="display:flex;">
              <div class="preview-slice-text" style="width:80%; border-bottom: 1px solid black; border-right: 1px solid black;">
                ${d["text"]}
              </div>
              <div class="preview-slice-label" style="border-bottom: 1px solid black;">
                ${d["label"]}
              </div>
            </div>`
          }
        ).join(' ') + 
          '</div>';

        var isSelected = that.highQualityTransforms.has(commonTransform);
        var isInspected = that.qualityMarkService.lowQualityTransforms.has(commonTransform);
        const row = {
          'transform_raw': that.transformNamesRaw(commonTransform),
          'Transform': html` 
          <div style="margin-top:0%; height:100%; vertical-align: middle;">
          <span>${that.transformNames(commonTransform)}</span>

          <div style="padding-top:8px; color:grey;">(${that.numMatchingInstances(commonTransform)} matching instances, </div>
          <div style="padding-top:8px; color:grey;">(${that.numSelectedInstances(commonTransform)} selected instances, </div>
          <div style="padding-top:4px; color:grey;"> ${that.numMatchingLowQInstances(commonTransform)} inspected; ${that.numMatchingHighQInstances(commonTransform)} high quality)
          </div> 
          ` ,
          'Mark all as high quality': html`
          
            <div style="margin-top:0%; width: 50%; text-align: center; border: 1px solid;"
                @click=${() => that.onSelectEnable(commonTransform, isSelected)}
              >
                <span style="visibility: ${isSelected ? "visible" : "hidden"};">
                  👍
                </span>
            </div>
          `,
          'Mark all as inspected': html`
          
            <div style="margin-top:0%; width: 50%; text-align: center; border: 1px solid;"
                @click=${() => that.onSelectInspected(commonTransform, isInspected)}
              >
                <span style="visibility: ${isInspected ? "visible" : "hidden"};">
                  👍
                </span>
            </div>
          `,
          'Transformed texts': html`${unsafeHTML(previewSlice)}`
        }
        rows.push(row);
        // console.log(row);
      });
    }


    return html`
      <div class="module-container">
        <div style="margin: 10px;">
    
        </div>
        <div class="module-results-area padded-container" style="margin-top: 10px;">
            <div class="results-holder">
            <lit-data-table class="table"
                .columnNames=${columns}
                .data=${rows}
            ></lit-data-table>

            
      <tr>
        <td>
          <div class="footer"  style="margin-bottom:12px">
                  <popup-container class='download-popup'>
                  <mwc-icon class='icon-button' slot='toggle-anchor'
                    title="Download CSV">
                    file_download
                  </mwc-icon>
                  Download CSV of enabled transforms
                  <div class='download-popup-controls'>
                    <label for="filename">Filename</label>
                    <input type="text" name="filename" value=${this.downloadFilename}
                    @input=${updateFilename} @keydown=${onEnter}>
                    <button class='filled-button nowrap' @click=${downloadCSV}
                      ?disabled=${!this.downloadFilename}>
                      Download rows
                    </button>
                  </div>
                </popup-container>
            <div class='footer-spacer'></div>
          </div>
        </td>
      </tr>
          </div>
        </div>
      </div>
    `
    // clang-format on
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'tx-transform-provenance-module': TxTransformProvenanceModule
  }
}
