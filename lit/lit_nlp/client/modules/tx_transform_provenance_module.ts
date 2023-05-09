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

  private transformNames(transformIndex : number) {
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


  private async onSelectEnable(commonTransform : number, isAlreadySelected: boolean) {
    // this.selectedInputData = selectedInputData.map(
    //   input => ({ idx: this.appState.getIndexById(input.id), ...input })
    // )
    // if (this.selectedInputData.length == 0) return
    // this.isLoading = true;

    // this.isLoading = false;
    console.log('[onSelectEnable] ' + commonTransform);

    if (!isAlreadySelected) {
      this.qualityMarkService.markHighQualityTransforms(commonTransform);
    } else {
      this.qualityMarkService.unmarkHighQualityTransforms(commonTransform);
    }
    // if (this.highQualityTransforms == undefined) {
    //   this.highQualityTransforms = new Set();
    // }
    // this.highQualityTransforms.add(commonTransform);
  }


  private async updateTransforms(incomingTransforms){
    console.log("[provenance] updateTransforms")
    console.log(incomingTransforms);
    this.commonTransforms = new Set(incomingTransforms);
  }

  private async updateHighQTransforms(qualityTransforms){
    console.log("[provenance] updateHighQTransforms")
    console.log(qualityTransforms);
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

    const columns: ColumnHeader[] = ['transform', 'enable', 'data'].map(
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
        selectedTransforms.push([this.transformNames(transform), "1"]);
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

    console.log("trigger regeneration of table...");
    console.log(this.commonTransforms);
    if (this.commonTransforms) {

      var dataSlices = this.filterBySimilarDataService.dataSliceOfTransformType;

      var that = this;
      this.commonTransforms.forEach(function(commonTransform) {

        const previewSliceData = dataSlices.get(commonTransform).slice(0, 3);

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
        const row = {
          'transform_raw': that.transformNames(commonTransform),
          'transform': html`<div style="height:100%"> 
          <div style="margin-top:50%; height:100%">
          ${that.transformNames(commonTransform)}
          </div> 
          </div>` ,
          'enable': html`<div
                        style="margin-top:50%; width: 50%; text-align: center; border: 1px solid"
                        @click=${() => that.onSelectEnable(commonTransform, isSelected)}
                      >
                        <span style="visibility: ${isSelected ? "visible" : "hidden"};">
                          👍
                        </span>
                      </div>`,
          'data': html`${unsafeHTML(previewSlice)}`
        }
        rows.push(row);
        console.log(row);
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
          <div class="footer">
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
