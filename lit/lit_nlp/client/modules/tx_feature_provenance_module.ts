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
import { customElement } from 'lit/decorators'
import { html, svg } from 'lit'
import { action, computed, observable } from 'mobx'

import { LitModule } from '../core/lit_module'

import { IndexedInput } from '../lib/types'
import { getTextWidth, getTokOffsets, sumArray } from '../lib/utils'
import { ColumnHeader, TableData, TableEntry } from '../elements/table';
import {unsafeHTML} from 'lit-html/directives/unsafe-html.js';


import { styles as sharedStyles } from '../lib/shared_styles.css'
import { styles } from './tx_feature_provenance_module.css'
import { getBrandColor } from '../lib/colors'
import { app } from '../core/app'
import { QualityMarkService } from '../services/qualityMark_service'
import { FilterBySimilarDataService } from '../services/filterBySimilarData_service'

@customElement('tx-feature-provenance-module')
export class TxFeatureProvenanceModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles]
  }

  static override title = 'Feature Provenance'
  static override numCols = 2
  static override collapseByDefault = false
  static override duplicateForModelComparison = false

  private readonly qualityMarkService = app.getService(QualityMarkService);
  private readonly filterBySimilarDataService = app.getService(FilterBySimilarDataService);

  static override template = () => {
    return html`<tx-feature-provenance-module></tx-feature-provenance-module>`
  }

  @observable private isLoading = false
  @observable private commonFeatures;
  @observable private highQualityFeatures;

  override firstUpdated() {
    this.reactImmediately(
      () => this.filterBySimilarDataService.commonFeatureTypes,
      commonFeatures => this.updateFeatures(commonFeatures)
    )

    this.reactImmediately(
      () => this.qualityMarkService.highQualityFeatures,
      highQualityFeature => this.updateHighQFeatures(highQualityFeature)
    )
  }


  private featuresNames(featureIndex : number) {
    var mapping = [
      'contains_accompanier',
            'contains_age',
            'contains_beneficiary',
            'contains_concession',
            'contains_condition',
            'contains_conjunctions',
            'contains_consist_of',
            'contains_coreferences',
            'contains_degree',
            'contains_destination',
            'contains_direction',
            'contains_domain',
            'contains_duration',
            'contains_example',
            'contains_exlamation',
            'contains_extent',
            'contains_frequency',
            'contains_imperative',
            'contains_instrument',
            'contains_interrogative_clause',
            'contains_location',
            'contains_manner',
            'contains_medium',
            'contains_mod',
            'contains_mode',
            'contains_name',
            'contains_negation',
            'contains_number',
            'contains_ord',
            'contains_part',
            'contains_path',
            'contains_polarity',
            'contains_polite',
            'contains_poss',
            'contains_purpose',
            'contains_quant',
            'contains_question',
            'contains_range',
            'contains_scale',
            'contains_source',
            'contains_subevent',
            'contains_time',
            'contains_topic',
            'contains_unit'
    ]
    return mapping[featureIndex];
  }

  private async onSelectEnable(commonFeature : number, isAlreadySelected: boolean) {
    // this.selectedInputData = selectedInputData.map(
    //   input => ({ idx: this.appState.getIndexById(input.id), ...input })
    // )
    // if (this.selectedInputData.length == 0) return
    // this.isLoading = true;

    // this.isLoading = false;
    console.log('[onSelectEnable] ' + commonFeature);

    if (!isAlreadySelected) {
      this.qualityMarkService.markHighQualityFeatures(commonFeature);
    } else {
      this.qualityMarkService.unmarkHighQualityFeatures(commonFeature);
    }
    // if (this.highQualityFeatures == undefined) {
    //   this.highQualityFeatures = new Set();
    // }
    // this.highQualityFeatures.add(commonFeature);
  }


  private async updateFeatures(incomingFeatures){
    console.log("[provenance] updateFeatures")
    console.log(incomingFeatures);
    this.commonFeatures = new Set(incomingFeatures);
  }

  private async updateHighQFeatures(qualityFeatures){
    console.log("[provenance] updateHighQFeatures")
    console.log(qualityFeatures);
    this.highQualityFeatures = new Set(qualityFeatures);
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

    const columns: ColumnHeader[] = ['feature', 'enable', 'data'].map(
      field => ({
        name: field,
        centerAlign: true,
      })
    )
    const rows = [];

    console.log("trigger regeneration of table...");
    console.log(this.commonFeatures);
    if (this.commonFeatures) {

      var dataSlices = this.filterBySimilarDataService.dataSliceOfFeatureType;

      var that = this;
      this.commonFeatures.forEach(function(commonFeature) {

        const previewSliceData = dataSlices.get(commonFeature).slice(0, 3);

        // wrap it in html
        const previewSlice = 
          '<div class="preview-slice-holder">' + 
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

        var isSelected = that.highQualityFeatures.has(commonFeature);
        const row = {
          'feature': that.featuresNames(commonFeature),
          'enable': html`<div
                        style="width: 50%; text-align: center; border: 1px solid"
                        @click=${() => that.onSelectEnable(commonFeature, isSelected)}
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
                
                exportEnabled
            ></lit-data-table>
          </div>
        </div>
      </div>
    `
    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-Feature-provenance-module': TxFeatureProvenanceModule
  }
}
