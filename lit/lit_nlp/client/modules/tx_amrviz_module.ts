// tslint:disable:no-new-decorators
import { customElement } from 'lit/decorators'
import { html, svg } from 'lit'
import { action, computed, observable } from 'mobx'

import { LitModule } from '../core/lit_module'

import { IndexedInput } from '../lib/types'

import { styles as sharedStyles } from '../lib/shared_styles.css'
import { styles } from './tx_amrviz_module.css'
import { getBrandColor } from '../lib/colors'
import { app } from '../core/app'

@customElement('tx-amrviz-module')
export class TxAmrVizModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles]
  }

  static override title = 'Tx AMR Viz'
  static override numCols = 2
  static override collapseByDefault = true
  static override duplicateForModelComparison = false

  static override template = () => {
    return html`<tx-amrviz-module></tx-amrviz-module>`
  }

  @observable private isLoading = false
  @observable private selectedInputData: IndexedInput[] = []
  // @observable private txProvTextFetch: object[] = []
  // @observable private txProvTraces: object[][] = []
  @observable private txProvAmr: object[] = []

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
          source: "TxAmrViz"
        }
      })
    )
    this.txProvAmr = []
    if (0 == this.selectedInputData.length) return
    this.isLoading = true
    const promise = this.apiService.getTxProvAmr(
      this.selectedInputData, undefined, 'Fetching AMR'
    )
    const res = await this.loadLatest('tx_prov_amr', promise)
    if (res == null) return
    this.txProvAmr = res.penman_graphs
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
    return html`
      <div class="module-container">
        ${
          this.txProvAmr.map(graph => {
            return html`
              <pre>
                ${graph}
              </pre>
            `
          })
        }
      </div>
    `

    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-amrviz-module': TxAmrVizModule
  }
}
