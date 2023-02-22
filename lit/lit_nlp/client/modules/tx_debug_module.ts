/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
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
import { customElement } from 'lit/decorators';
import { html, PropertyValueMap } from 'lit';
import { observable } from 'mobx';

import {app} from '../core/app';

import { LitModule } from '../core/lit_module';
import {SelectionService} from '../services/selection_service';

import { IndexedInput } from '../lib/types'

import { styles as sharedStyles } from '../lib/shared_styles.css';
import { styles } from './tx_debug_module.css';
import { defaultValueByField } from '../lib/types';
import { QualityMarkService } from '../services/qualityMark_service';
import { ColumnHeader, TableData } from '../elements/table';

@customElement('tx-debug-module')
export class TxDebugModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles];
  }

  static override title = 'Tx Debug';
  static override numCols = 2;
  static override collapseByDefault = true;
  static override duplicateForModelComparison = false;

  private readonly qualityMarkService = app.getService(QualityMarkService);

  static override template = () => {
    return html`<tx-debug-module></tx-debug-module>`;
  };

  @observable private isLoading = false
  // @observable private selectionType: "default" | "high_Q" | "low_Q" = "default"
  // @observable private selectedInputData: IndexedInput[] = []
  @observable private highQualityInputData: IndexedInput[] = []
  @observable private lowQualityInputData: IndexedInput[] = []
  @observable.struct private txProvStats = {schema: {fields: [] as any[]}, data: [] as any[]}
  // @observable private selectedData: string[] = []

  override async firstUpdated() {
    // void this.apiService.getTxProvStats([{
    //   id: `${1}`,
    //   idx: 1,
    //   data: { label: 1 },
    //   meta: {}
    // }], undefined, 'Fetching tx provenance stats')
    // this.reactImmediately(_ => this.selectionService.selectedIds,
    //   primarySelectedInputData => {
    //     this.selectedData = primarySelectedInputData;
    //   }
    // )
    this.reactImmediately(
      () => this.qualityMarkService.highQualityIndices,
      highQualityIndices => this.onUpdateHighQualityIndices(highQualityIndices)
    )
    this.reactImmediately(
      () => this.qualityMarkService.lowQualityIndices,
      lowQualityIndices => this.onUpdateLowQualityIndices(lowQualityIndices)
    )
    // this.txProvStats = {schema: {fields: []}, data: []}
    // this.isLoading = true
    // const promise = this.apiService.getTxProvStats(
    //   [] as any, undefined, 'Fetching tx provenance stats'
    // )
    // const res = await this.loadLatest('tx_prov_stats', promise)
    // if (res == null) return
    // this.txProvStats = res
    // this.isLoading = false
    // debugger
  }

  private async onUpdateHighQualityIndices(highQualityIndices: Set<number>) {
    this.highQualityInputData = Array.from(highQualityIndices).map(
      idx => ({
        idx: idx,
        id: idx.toString(),
        data: {
          idx: idx,
          id: idx.toString(),
          label: 1
        },
        meta: {
          source: "TxDebug"
        }
      })
    )
    // if (this.selectionType != "high_Q") return
    this.txProvStats = {schema: {fields: []}, data: []}
    if (this.highQualityInputData.length == 0) return
    this.isLoading = true
    const promise = this.apiService.getTxProvStats(
      this.highQualityInputData, undefined, 'Fetching tx provenance stats'
    )
    const res = await this.loadLatest('tx_prov_stats', promise)
    if (res == null) return
    this.txProvStats = res
    this.isLoading = false
  }

  private async onUpdateLowQualityIndices(lowQualityIndices: Set<number>) {
    this.lowQualityInputData = Array.from(lowQualityIndices).map(
      idx => ({
        idx: idx,
        id: idx.toString(),
        data: {
          idx: idx,
          id: idx.toString(),
          label: 0
        },
        meta: {
          source: "TxDebug"
        }
      })
    )
    // if (this.selectionType != "low_Q") return
    this.txProvStats = {schema: {fields: []}, data: []}
    if (this.lowQualityInputData.length == 0) return
    this.isLoading = true
    const promise = this.apiService.getTxProvStats(
      this.lowQualityInputData, undefined, 'Fetching tx provenance stats'
    )
    const res = await this.loadLatest('tx_prov_stats', promise)
    if (res == null) return
    this.txProvStats = res
    this.isLoading = false
    // debugger
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

    if (this.lowQualityInputData.length == 0 && this.highQualityInputData.length == 0) {
      return html`
        <div class="module-container">
          <p>
            Mark atleast 1 row 👍 (high_Q) / 👎 (low_Q)
          </p>
        </div>
      `
    }

    // const columns: ColumnHeader[] = [
    //   {name: "Tx Decription", centerAlign: true},
    //   {name: "Sus. score", centerAlign: true, searchDisabled: true},
    //   {name: "Misclassify prob.", centerAlign: true, searchDisabled: true},
    // ]

    const columns: ColumnHeader[] = this.txProvStats.schema.fields.map(
      field => ({
        name: field.name,
        centerAlign: true,
        searchDisabled: ["integer", "number"].includes(field.type)
      })
    )


    // const tableData: TableData[] = [
    //   ["data[0][0]", "data[0][1]", "data[0][2]"],
    //   ["data[1][0]", html`<span style="background:orange;">data[1][1]</span>`, "data[1][2]"],
    //   ["data[2][0]", "data[2][1]", html`<span style="background:lightgreen;">data[1][1]</span>`],
    // ]

    // debugger

    return html`
      <div class="module-container">
        <div class="module-results-area">
          <lit-data-table
            .data=${this.txProvStats.data}
            .columnNames=${columns}
            searchEnabled
          />
        </div>
      </div>
    `;

    // return html`
    //   <div class="module-container">
    //     <div style="display: float;">
    //       <select class="dropdown" @change=${() => alert("changed!")}>
    //         <option value="default">default</option>
    //         <option value="high quality">👍 — high quality</option>
    //         <option value="low quality">👎 — low quality</option>
    //       </select>
    //     </div>
    //     <div class="module-results-area">
    //       <div>
    //         <ul>
    //           <li>👍</li>
    //           ${Array.from(this.qualityMarkService.highQualityIndices).map(
    //             id => html`<li>${id}</li>`
    //           )}
    //         <ul>
    //       </div>
    //       <div>
    //         <ul>
    //           <li>👎</li>
    //           ${Array.from(this.qualityMarkService.lowQualityIndices).map(
    //             id => html`<li>${id}</li>`
    //           )}
    //         </ul>
    //       </div>
    //       <lit-data-table
    //         .data=${tableData}
    //         .columnNames=${columns}
    //         searchEnabled
    //       />
    //     </div>
    //   </div>
    // `;
    // clang-format on
  }

  private txProvStats_mock = {
      "schema": {
          "fields": [
              {
                  "name": "transform",
                  "type": "string"
              },
              {
                  "name": "total_freq",
                  "type": "integer"
              },
              {
                  "name": "label_ratio",
                  "type": "number"
              },
              {
                  "name": "impact_ratio",
                  "type": "number"
              },
              {
                  "name": "fail_num",
                  "type": "integer"
              },
              {
                  "name": "pass_num",
                  "type": "integer"
              },
              {
                  "name": "sus_score",
                  "type": "integer"
              },
              {
                  "name": "misclassify_prob",
                  "type": "number"
              }
          ],
          "primaryKey": [
              "transform"
          ],
          "pandas_version": "1.4.0"
      },
      "data": [
          {
              "transform": "('replace', ('exclude',), ('neutral',))",
              "total_freq": 70,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1285714286
          },
          {
              "transform": "('replace', ('neg',), ('neg',))",
              "total_freq": 179,
              "label_ratio": 0.0055865922,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 1,
              "sus_score": 0,
              "misclassify_prob": 0.2346368715
          },
          {
              "transform": "('replace', ('neutral',), ('neutral',))",
              "total_freq": 917,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1603053435
          },
          {
              "transform": "('replace', ('pos',), ('neutral',))",
              "total_freq": 114,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.201754386
          },
          {
              "transform": "('replace', ('pos',), ('pos',))",
              "total_freq": 151,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1523178808
          },
          {
              "transform": "('replace', ('neutral',), ('neg',))",
              "total_freq": 54,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2592592593
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neutral', 'neutral'))",
              "total_freq": 49,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1428571429
          },
          {
              "transform": "('replace', ('neg', 'neutral'), ('neutral', 'neutral'))",
              "total_freq": 7,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1428571429
          },
          {
              "transform": "('replace', ('neg',), ('neutral',))",
              "total_freq": 95,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2105263158
          },
          {
              "transform": "('replace', ('neutral',), ('exclude',))",
              "total_freq": 19,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2105263158
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neg', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('pos', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('neutral', 'neutral'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.3333333333
          },
          {
              "transform": "('replace', ('neutral', 'pos'), ('neutral', 'pos'))",
              "total_freq": 5,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2
          },
          {
              "transform": "('replace', ('neg',), ('pos',))",
              "total_freq": 15,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.3333333333
          },
          {
              "transform": "('replace', ('neutral', 'pos', 'exclude'), ('neutral', 'neutral', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('pos', 'neutral'))",
              "total_freq": 5,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2
          },
          {
              "transform": "('replace', ('neutral',), ('pos',))",
              "total_freq": 50,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2
          },
          {
              "transform": "('replace', ('pos',), ('neg',))",
              "total_freq": 19,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1578947368
          },
          {
              "transform": "('replace', ('pos', 'neutral'), ('neutral', 'neutral'))",
              "total_freq": 23,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1304347826
          },
          {
              "transform": "('replace', ('neg', 'neutral'), ('neg', 'neutral'))",
              "total_freq": 15,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.0666666667
          },
          {
              "transform": "('replace', ('neutral', 'exclude'), ('neutral', 'neutral'))",
              "total_freq": 6,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1666666667
          },
          {
              "transform": "('replace', ('neutral', 'neg', 'neutral'), ('neutral', 'neg', 'neutral'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'pos', 'neutral'), ('neutral', 'pos', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'neutral'), ('pos', 'neutral'))",
              "total_freq": 19,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2105263158
          },
          {
              "transform": "('replace', ('exclude',), ('pos',))",
              "total_freq": 11,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.3636363636
          },
          {
              "transform": "('replace', ('exclude',), ('exclude',))",
              "total_freq": 39,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2820512821
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('neutral', 'neg'))",
              "total_freq": 10,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.1
          },
          {
              "transform": "('replace', ('neutral', 'exclude', 'pos'), ('neutral', 'pos', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neg', 'neutral'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'pos'), ('neg', 'neutral'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.5
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('pos', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'exclude'), ('neutral', 'exclude'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral', 'neutral'), ('neutral', 'neutral', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('exclude', 'neutral'), ('neutral', 'neutral'))",
              "total_freq": 5,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2
          },
          {
              "transform": "('replace', ('neutral', 'pos'), ('neg', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('exclude', 'neutral'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'pos'), ('neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('exclude', 'neg', 'neutral'), ('exclude', 'neg', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'neg'), ('pos', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'pos'), ('pos', 'neutral'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.6666666667
          },
          {
              "transform": "('replace', ('neutral', 'neutral', 'pos'), ('neutral', 'neg', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'neg'), ('neutral', 'neg'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'pos'), ('neutral', 'neutral'))",
              "total_freq": 4,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'neg'), ('neg', 'neg'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.6666666667
          },
          {
              "transform": "('replace', ('neutral', 'exclude', 'neutral'), ('neutral', 'exclude', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'neutral'), ('pos', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'pos'), ('exclude', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'neutral'), ('exclude', 'neutral'))",
              "total_freq": 5,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.2
          },
          {
              "transform": "('replace', ('pos',), ('exclude',))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.5
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neg', 'pos'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'neutral'), ('neg', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('pos', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'neg'), ('exclude', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('neg', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'neutral'), ('neutral', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'neutral', 'neutral'), ('neutral', 'neutral', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'pos'), ('neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'exclude', 'exclude'), ('neutral', 'exclude', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('exclude', 'neutral'), ('pos', 'neutral'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'neutral', 'pos'), ('neutral', 'neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'exclude'), ('pos', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neutral', 'pos'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0.3333333333
          },
          {
              "transform": "('replace', ('neg', 'neutral'), ('pos', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('pos', 'neutral'), ('neutral', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'neg'), ('exclude', 'neg'))",
              "total_freq": 3,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neg'), ('neutral', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neg', 'neutral'), ('neutral', 'neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'pos', 'neutral'), ('neg', 'neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'exclude'), ('pos', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neutral', 'exclude'))",
              "total_freq": 2,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neg', 'neutral'), ('neg', 'pos'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'pos'), ('neutral', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('pos', 'neutral', 'neutral'), ('neutral', 'neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('neutral', 'exclude'), ('exclude', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'exclude'), ('exclude', 'exclude'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('neutral', 'neutral'), ('neutral', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 1
          },
          {
              "transform": "('replace', ('neg', 'pos'), ('neutral', 'neg'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          },
          {
              "transform": "('replace', ('exclude', 'exclude'), ('neutral', 'neutral'))",
              "total_freq": 1,
              "label_ratio": 0,
              "impact_ratio": 0,
              "fail_num": 0,
              "pass_num": 0,
              "sus_score": 0,
              "misclassify_prob": 0
          }
      ]
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-debug-module': TxDebugModule;
  }
}
