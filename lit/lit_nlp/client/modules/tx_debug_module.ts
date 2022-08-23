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

import { styles as sharedStyles } from '../lib/shared_styles.css';
import { styles } from './tx_debug_module.css';
import { defaultValueByField } from '../lib/types';
import { QualityMarkService } from '../services/qualityMark_service';

@customElement('tx-debug-module')
export class TxDebugModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles];
  }

  static override title = 'Tx Debug';
  static override numCols = 2;
  static override collapseByDefault = false;
  static override duplicateForModelComparison = false;

  private readonly qualityMarkService = app.getService(QualityMarkService);
  
  static override template = () => {
    return html`<tx-debug-module></tx-debug-module>`;
  };

  @observable private selectedData: string[] = []

  override firstUpdated() {
    this.reactImmediately(_ => this.selectionService.selectedIds,
      primarySelectedInputData => {
        this.selectedData = primarySelectedInputData;
      }
    )
  }

  
  override render() {
    // clang-format off
    return html`
      <div class="module-container">
        <div style="display: float;">
          <select class="dropdown" @change=${() => alert("changed!")}>
            <option value="default">default</option>
            <option value="high quality">👍 — high quality</option>
            <option value="low quality">👎 — low quality</option>
          </select>
        </div>
        <div class="module-results-area">
          <div>
            <ul>
              <li>👍</li>
              ${Array.from(this.qualityMarkService.highQualityIndices).map(
                id => html`<li>${id}</li>`
              )}
            <ul>
          </div>
          <br>
          <div>
            <ul>
              <li>👎</li>
              ${Array.from(this.qualityMarkService.lowQualityIndices).map(
                id => html`<li>${id}</li>`
              )}
            </ul>
          </div>
        </div>
      </div>
    `;
    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-debug-module': TxDebugModule;
  }
}
