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

  @property({type: String}) downloadFilename: string = 'feature_provenance_enabled.csv';

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

  private featuresNamesRaw(featureIndex : number) {
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
      'contains_quant'
    ]
    return mapping[featureIndex];
  }

  private featuresNames(featureIndex : number) {
    var mapping = [
      // 'contains_accompanier', 
      'Contains accompanier (e.g., "with a police escort")',
            // 'contains_age',
      'Describes a temporal quantity (e.g., "the 15-year-old law")',
            // 'contains_beneficiary',
            'Contains beneficiary (e.g. "for his mother")',

            // 'contains_concession',
            'Contains a concession (e.g. "although it rained")',
            // 'contains_condition',
            'Contains a condition (e.g. "if it rains")',
            // 'contains_conjunctions',
            'Contains a conjunction (e.g., "and", "either")',
            // 'contains_consist_of',
            'Describes a "consists of" relation (e.g., "a ring of gold") ',
            // 'contains_coreferences',
            'Contains a pronoun referencing a person (e.g., "he", "she", "they")',
            // 'contains_degree',
            'Contains degree, such as "very tall" or "extremely happy", that modifies the intensity',
            // 'contains_destination',
            'Contains destination, such as "to the store"',
            // 'contains_direction',
            'Contains a direction, such as "north" or "downward',
            // 'contains_domain',
            'Contains words used in constructions, e.g., "is a lawyer"',
            // 'contains_duration',
            'Describes a duration, e.g., "about 20 minutes"',
            // 'contains_example',
            'Contains an example, e.g., "companies like IBM"',
            // 'contains_exlamation',
            'Contains interjections such as "wow" that expresses emotions',
            // 'contains_extent',
            'Contains a description of an extent, e.g. "for 120 miles", "forever"',
            // 'contains_frequency',
            'Contains frequency, e.g. "three times"',
            // 'contains_imperative',
            'Has an imperative mode, e.g., using "Please"',

            // 'contains_instrument',
            'Has a description of a physical object, e.g. "with a fork"',
            // 'contains_interrogative_clause',
            'Contains an interrogative clause, e.g., "whether or not"',
            
            // 'contains_location',
            'Has a description of a location, e.g., "in Los Angeles"',
            // 'contains_manner',
            'Has a description how something is done, e.g., "in a creative way"',
            // 'contains_medium',
            'Contains a medium of communication, e.g., "in the newspaper"',
            // 'contains_mod',
            'Has a modifier on a noun, e.g., "old man"', 
            // 'contains_mode',
            'Has a mode, e.g., an imperative term or expressive term, "Yippee"', 
            // 'contains_name',
            'Contains a name, e.g. France', 
            // 'contains_negation',
            'Has a negation, e.g. "not"',
            // 'contains_number',
            'Contains a number',
            // 'contains_ord',
            'Has an ordinal term, e.g., "second planet"', 
            // 'contains_part',
            'Has a description of a component or part, e.g. "roof of the house"',
            // 'contains_path',
            'Has a description of a path, e.g. "via Paris"',
            // 'contains_polarity',
            'Contains a term indicating polarity, e.g. "no information"',
            // 'contains_polite',
            'Contains a polite term, e.g. "kindly"',
            // 'contains_poss',
            'Has a general form of posession, e.g., "His health"', 
            // 'contains_purpose',
            'Describes the purpose, e.g. "in order to breathe."', 
            // 'contains_quant',
            'Describes a quantity',

            // 'contains_question',
            'Contains a question', 
            // 'contains_range',
            'Describes a range, e.g., "in 10 years"',
            // 'contains_scale',
            'Contains a scale used for measuring quantity', 
            // 'contains_source',
            'Contains a description of a source, e.g. "from Houston"', 
            // 'contains_subevent',
            'Describes a subevent occuring with another event, e.g. "I pass the resort on my way to work."',
            // 'contains_time',
            'Contains a description of a time, e.g., "yesterday"', 
            // 'contains_topic',
            'Describes a topic, e.g., "about the case"', 
            // 'contains_unit'
            'Has a unit',
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
    // console.log('[onSelectEnable] ' + commonFeature);

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
    // console.log("[provenance] updateFeatures")
    // console.log(incomingFeatures);
    this.commonFeatures = new Set(incomingFeatures);
  }

  private async updateHighQFeatures(qualityFeatures){
    // console.log("[provenance] updateHighQFeatures")
    // console.log(qualityFeatures);
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


    const updateFilename = (e: Event) => {
      // tslint:disable-next-line:no-any
      this.downloadFilename = (e as any).target.value as string;
    };

    const getSelectedFeatures = () => {
      const selectedTransforms = [];
      for (const transform of this.highQualityFeatures) {
        selectedTransforms.push([this.featuresNamesRaw(transform), "1"]);
      }
      return selectedTransforms;
    }

    const csvContent = function() {
      return papa.unparse(
        {fields: ['features'], data: getSelectedFeatures()},
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


    if (this.commonFeatures) {

      var dataSlices = this.filterBySimilarDataService.dataSliceOfFeatureType;

      var that = this;
      this.commonFeatures.forEach(function(commonFeature) {

        const previewSliceData = dataSlices.get(commonFeature).slice(0, 3);

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

        var isSelected = that.highQualityFeatures.has(commonFeature);
        const row = {
          'feature_raw': that.featuresNamesRaw(commonFeature),
          'feature': 
            html`
            <div style="margin-top:0%; height:100%">
            ${that.featuresNames(commonFeature)}
            </div> `,
          'enable': html`
          
            <div style="margin-top:0%; width: 50%; text-align: center; border: 1px solid"
              @click=${() => that.onSelectEnable(commonFeature, isSelected)}
            >
              <span style="visibility: ${isSelected ? "visible" : "hidden"};">
                👍
              </span>
            </div>`,
          'data': html`${unsafeHTML(previewSlice)}`
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
    'tx-Feature-provenance-module': TxFeatureProvenanceModule
  }
}
