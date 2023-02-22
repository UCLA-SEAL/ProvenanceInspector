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


import { styles as sharedStyles } from '../lib/shared_styles.css'
import { styles } from './tx_textfetch_module.css'
import { getBrandColor } from '../lib/colors'
import { app } from '../core/app'

@customElement('tx-textfetch-module')
export class TxTextFetchModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles]
  }

  static override title = 'Tx TextFetch'
  static override numCols = 2
  static override collapseByDefault = true
  static override duplicateForModelComparison = false

  static override template = () => {
    return html`<tx-textfetch-module></tx-textfetch-module>`
  }

  @observable private isLoading = false
  @observable private selectedInputData: IndexedInput[] = []
  @observable private txProvTextFetch: object[] = []
  // @observable private txProvTraces: object[][] = []

  override firstUpdated() {
    this.reactImmediately(
      () => this.selectionService.selectedInputData,
      selectedInputData => this.onUpdateSelection(selectedInputData)
    )
  }

  private async onUpdateSelection(selectedInputData: IndexedInput[]) {
    this.selectedInputData = selectedInputData.map(
      input => ({
        id: input.id,
        idx: this.appState.getIndexById(input.id),
        data: {
          id: input.id,
          idx: this.appState.getIndexById(input.id),
          text: this.appState.getExamplesById([input.id])[0].data.sentence
        },
        meta: {
          source: "TxTextFetch"
        }
      })
    )
    this.txProvTextFetch = []
    if (0 == this.selectedInputData.length) return
    this.isLoading = true
    const promise = this.apiService.getTxProvTextFetch(
      this.selectedInputData, undefined, 'Fetching tx provenance textfetch'
    )
    const res = await this.loadLatest('tx_prov_textfetch', promise)
    if (res == null) return
    this.txProvTextFetch = res
    this.isLoading = false
  }


  override render() {
    // clang-format off
    if (this.isLoading) {
      return html`
        <div class="module-container">
          <p>
            L o a d i n g...
          </p>
        </div>
      `
    }
    // return html`
    //   <div class="module-container">
    //     <pre>
    //       ${JSON.stringify(this.txProvTextFetch, null, 4)}
    //     </pre>
    //   </div>
    // `

    const filterText = (e: Event, text_id: Number) => {
      const f: any = document.querySelector("body > lit-app").shadowRoot.querySelector("lit-modules").shadowRoot.querySelector("#widget-group-upper-0-0").shadowRoot.querySelector("div > div > div.holder > lit-widget > data-table-module").shadowRoot.querySelector("div > div.module-results-area > lit-data-table").shadowRoot.querySelector("#index > div.column-header > div > div.menu-button-container > mwc-icon")
      f.click()

      const input: any = document.querySelector("body > lit-app").shadowRoot.querySelector("lit-modules").shadowRoot.querySelector("#widget-group-upper-0-0").shadowRoot.querySelector("div > div > div.holder > lit-widget > data-table-module").shadowRoot.querySelector("div > div.module-results-area > lit-data-table").shadowRoot.querySelector("#index > div.togglable-menu-holder > input")
      input.value = text_id
      input.dispatchEvent(new Event("input"))
      f.click()
    }

    return html`
      <div class="module-container">
        <ul>
          <li>
            <p>
              <span style="color: blue"> S E M A N T I C </span>
              <ul>
                ${(() => {
                  return (this.txProvTextFetch as any)?.semantic?.map(
                    item => html`<li>
                      <button @click=${(e: Event) => filterText(e, item.text_id)}>
                        Text [${item.text_id}]
                      </button>
                      <pre>${JSON.stringify(item, null, 4)}</pre>
                    </li>`
                  )
                })()}
              </ul>
            </p>
          </li>
          <li>
            <p>
            <span style="color: blue"> S Y N T A C T I C </span>
              <ul>
                ${(() => {
                  return (this.txProvTextFetch as any)?.syntactic?.map(
                    item => html`<li>
                      <button @click=${(e: Event) => filterText(e, item.text_id)}>
                        Text [${item.text_id}]
                      </button>
                      <pre>${JSON.stringify(item, null, 4)}</pre>
                    </li>`
                  )
                })()}
              </ul>
            </p>
          </li>
          <li>
            <p>
            <span style="color: blue"> M O R P H O L O G I C A L </span>
              <ul>
                ${(() => {
                  return (this.txProvTextFetch as any)?.morphological?.map(
                    item => html`<li>
                      <button @click=${(e: Event) => filterText(e, item.text_id)}>
                        Text [${item.text_id}]
                      </button>
                      <pre>${JSON.stringify(item, null, 4)}</pre>
                    </li>`
                  )
                })()}
              </ul>
            </p>
          </li>
        </ul>
      </div>
    `

    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-textfetch-module': TxTextFetchModule
  }
}
