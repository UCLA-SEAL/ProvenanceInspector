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

import {IndexedInput, ModelInfoMap, Spec} from '../lib/types'
import {doesOutputSpecContain, findSpecKeys, getTextWidth, getTokOffsets, sumArray} from '../lib/utils'


import { styles as sharedStyles } from '../lib/shared_styles.css'
import { styles } from './tx_provenance_module.css'
import { getBrandColor } from '../lib/colors'

@customElement('tx-provenance-module')
export class TxProvenanceModule extends LitModule {

  static override get styles() {
    return [sharedStyles, styles]
  }

  static override title = 'Tx Provenance'
  static override numCols = 2
  static override collapseByDefault = false
  static override duplicateForModelComparison = false

  static override template = () => {
    return html`<tx-provenance-module></tx-provenance-module>`
  }

  @observable private selectedData: string[] = []

  override firstUpdated() {
    this.reactImmediately(_ => this.selectionService.selectedIds,
      primarySelectedInputData => {
        this.selectedData = primarySelectedInputData;
      }
    )
  }

  /**
 * Render the actual lines between tokens to show the attention values.
 */
  private renderAttnLines(
    visHeight: number, spaceWidth: number, pad: number,
    inTokWidths: number[], outTokWidths: number[]
  ) {
    const inTokOffsets = getTokOffsets(inTokWidths, spaceWidth)
    const outTokOffsets = getTokOffsets(outTokWidths, spaceWidth)
    
    const x1 = (i: number) => outTokOffsets[i] + (outTokWidths[i] / 2)
    const y1 = pad
    const x2 = (i: number) => inTokOffsets[i] + (inTokWidths[i] / 2)
    const y2 = pad + visHeight

    // clang-format off
    return svg`
      ${inTokWidths.map((_, i) => {
        return svg`
          <line
            x1=${x1(i)}
            y1=${y1}
            x2=${x2(i)}
            y2=${y2}
            stroke="${getBrandColor('cyea', '600').color}"
            stroke-width=2>
          </line>
        `
      })}
    `
    // clang-format on
  }

  private renderAttnHead(item: string) {

    const inToks = item.split(" ").filter(token => token.trim().length > 0)
    const outToks = item.split(" ").filter(token => token.trim().length > 0)

    const fontFamily = "'Share Tech Mono', monospace"
    const fontSize = 12
    const defaultCharWidth = 6.5
    const font = `${fontSize}px ${fontFamily}`

    const inTokWidths = inToks.map(tok => getTextWidth(tok, font, defaultCharWidth))
    const outTokWidths = outToks.map(tok => getTextWidth(tok, font, defaultCharWidth))
    const spaceWidth = getTextWidth(' ', font, defaultCharWidth)

    // Height of the attention visualization part.
    const visHeight = 100

    // Vertical pad between attention vis and words.
    const pad = 10

    // Calculate the full width and height.
    const inTokWidth = sumArray(inTokWidths) + (inToks.length - 1) * spaceWidth
    const outTokWidth = sumArray(outTokWidths) + (outToks.length - 1) * spaceWidth
    const width = Math.max(inTokWidth, outTokWidth)
    const height = visHeight + (fontSize * 2) + (pad * 4)
    const inTokOffsets = getTokOffsets(inTokWidths, spaceWidth)
    const outTokOffsets = getTokOffsets(outTokWidths, spaceWidth)

    const toksRender = (tok: string, i: number, isInputToken: boolean) => {
      const x = isInputToken ? inTokOffsets[i] : outTokOffsets[i]
      const y = isInputToken ? visHeight + 4 * pad : pad * 2
      const text = svg`${tok}`
      return svg`<text x=${x} y=${y}>${text}</text>`
    }

    // clang-format off
    return svg`
      <svg width=${width} height=${height} font-family="${fontFamily}" font-size="${fontSize}px">
        ${outToks.map((tok, i) => toksRender(tok, i, false))}
        ${this.renderAttnLines(visHeight, spaceWidth, 2.5 * pad, inTokWidths, outTokWidths)}
        ${inToks.map((tok, i) => toksRender(tok, i, true))}
      </svg>
    `
    // clang-format on
  }

  override render() {
    // clang-format off
    return html`
      <div class="module-container">
        <div class="module-results-area padded-container">
          ${this.selectedData.map((item) => {
            return this.renderAttnHead(
              this.appState.getCurrentInputDataById(item)?.data["sentence"]
            )
          })}
        </div>
      </div>
    `
    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-provenance-module': TxProvenanceModule
  }
}
