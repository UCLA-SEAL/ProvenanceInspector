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
import { styles } from './tx_provenance_module.css'
import { getBrandColor } from '../lib/colors'
import { app } from '../core/app'
import { QualityMarkService } from '../services/qualityMark_service'

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

  static override template = () => {
    return html`<tx-feature-provenance-module></tx-feature-provenance-module>`
  }

  @observable private isLoading = false
  @observable private selectionType: "default" | "high_Q" | "low_Q" = "default"
  @observable private selectedInputData: IndexedInput[] = []
  @observable private highQualityInputData: IndexedInput[] = []
  @observable private lowQualityInputData: IndexedInput[] = []
  @observable private txProvTraces: object[][] = []

  override firstUpdated() {
    this.reactImmediately(
      () => this.selectionService.selectedInputData,
      selectedInputData => this.onUpdateSelection(selectedInputData)
    )
    this.reactImmediately(
      () => this.qualityMarkService.highQualityIndices,
      highQualityIndices => this.onUpdateHighQualityIndices(highQualityIndices)
    )
    this.reactImmediately(
      () => this.qualityMarkService.lowQualityIndices,
      lowQualityIndices => this.onUpdateLowQualityIndices(lowQualityIndices)
    )
  }

  private async onUpdateSelection(selectedInputData: IndexedInput[]) {
    this.selectedInputData = selectedInputData.map(
      input => ({ idx: this.appState.getIndexById(input.id), ...input })
    )
    if (this.selectionType != "default") return
    this.txProvTraces = []
    if (this.selectedInputData.length == 0) return
    this.isLoading = true
    const promise = this.apiService.getTxProvTraces(
      this.selectedInputData, undefined, 'Fetching tx provenance traces'
    )
    const res = await this.loadLatest('tx_prov_traces', promise)
    if (res == null) return
    this.txProvTraces = res
    this.isLoading = false
  }

  private async onUpdateHighQualityIndices(highQualityIndices: Set<number>) {
    this.highQualityInputData = Array.from(highQualityIndices).map(
      idx => ({
        idx: idx,
        id: idx.toString(),
        data: {},
        meta: {}
      })
    )
    if (this.selectionType != "high_Q") return
    this.txProvTraces = []
    if (this.highQualityInputData.length == 0) return
    this.isLoading = true
    const promise = this.apiService.getTxProvTraces(
      this.highQualityInputData, undefined, 'Fetching tx provenance traces'
    )
    const res = await this.loadLatest('tx_prov_traces', promise)
    if (res == null) return
    this.txProvTraces = res
    this.isLoading = false
  }

  private async onUpdateLowQualityIndices(lowQualityIndices: Set<number>) {
    this.lowQualityInputData = Array.from(lowQualityIndices).map(
      idx => ({
        idx: idx,
        id: idx.toString(),
        data: {},
        meta: {}
      })
    )
    if (this.selectionType != "low_Q") return
    this.txProvTraces = []
    if (this.lowQualityInputData.length == 0) return
    this.isLoading = true
    const promise = this.apiService.getTxProvTraces(
      this.lowQualityInputData, undefined, 'Fetching tx provenance traces'
    )
    const res = await this.loadLatest('tx_prov_traces', promise)
    if (res == null) return
    this.txProvTraces = res
    this.isLoading = false
  }

  private onChangeSelectionType(e: Event) {
    const selectionType = (e.target as HTMLSelectElement).value
    
    if (selectionType == "default") {
      this.selectionType = selectionType
      this.onUpdateSelection(this.selectedInputData)
    }
    else if (selectionType == "high_Q") {
      this.selectionType = selectionType
      this.onUpdateHighQualityIndices(this.qualityMarkService.highQualityIndices)
    }
    else if (selectionType == "low_Q") {
      this.selectionType = selectionType
      this.onUpdateLowQualityIndices(this.qualityMarkService.lowQualityIndices)
    }
    else {
      throw new Error("Invalid selection type");
    }
  }

  private renderTrace(trace: object[], sno: number) {
    if (trace.length < 4 || trace.length%3 != 1)
      throw new Error(`Bad/invalid trace. Trace length ${trace.length} NOT of kind 3k+4`)

    const fontFamily = "'Share Tech Mono', monospace"
    const fontSize = 12
    const defaultCharWidth = 6.5
    const font = `${fontSize}px ${fontFamily}`
    const spaceWidth = getTextWidth(' ', font, defaultCharWidth)
    // Height of the attention visualization part.
    const visHeight = 75
    // Vertical pad between attention vis and words.
    const pad = 10

    const tokenizedTexts: any[] = []
    let traceWidth = 0;
    let traceHeight = 0;
    let prevTokenizedText: any = undefined
    for (let i = 0; i < trace.length; i += 3) {
      const [textId, text, label] = trace[i] as [number, string, number]
      const tokens = (
        text
          .split(' ')
          .filter(token => {
            let nonAlphaNum = new Set([
              ",",
              ".",
              "'",
              ";",
              ":",
              "?",
              '"',
              "(",
              ")",
              "-",
            ])
            return (
              (token.length > 1 && (false == new Set(["...", "--"]).has(token))) ||
              (token.length == 1 && (false == nonAlphaNum.has(token)))
            )
          })
      )
      const tokenWidths =  tokens.map(tok => getTextWidth(tok, font, defaultCharWidth))
      const tokenOffsets = getTokOffsets(tokenWidths, spaceWidth)
      const verticalOffset = (
        prevTokenizedText
          ? prevTokenizedText.verticalOffset + fontSize + visHeight + (4 * pad)
          : (2 * pad)
      )
      const width = sumArray(tokenWidths) + (tokens.length - 1) * spaceWidth
      traceWidth = Math.max(traceWidth, width)
      traceHeight = verticalOffset
      const inbound: any = prevTokenizedText?.outbound
      const outbound: any = (i+2 < trace.length) ? [trace[i+1], trace[i+2]] : undefined
      const tokenizedText = {
        prevTokenizedText: prevTokenizedText ??  {...prevTokenizedText},
        textId,
        label,
        tokens,
        tokenWidths,
        tokenOffsets,
        verticalOffset,
        width,
        inbound,
        outbound,
        render() {
          const outSet = new Set<number>()
          const txSet = new Set<number>()
          if (inbound && inbound.length > 0 && inbound[1].length > 0) {
            let [[_, ...edits]] = inbound[1]
            edits.forEach((edit: any) => {
              txSet.add(edit[0])
            })
          }
          if (outbound && outbound.length > 0 && outbound[1].length > 0) {
            let [[_, ...edits]] = outbound[1]
            edits.forEach((edit: any) => {
              outSet.add(edit[0])
              txSet.add(edit[0])
            })
          }

          const renderedTokens = (
            tokens.map((token, k) => {
              const x = tokenOffsets[k]
              const y =  verticalOffset
              const text = svg`${token}`
              if (txSet.has(k)) {
                return svg`<text x=${x} y=${y} filter="url(#yellow)">${text}</text>`
              }
              else {
                return svg`<text x=${x} y=${y}>${text}</text>`
              }
            }).concat(
              svg`
                <text
                  x=${tokenOffsets[tokenOffsets.length - 1]
                      + tokenWidths[tokenWidths.length - 1]
                      + 5 * spaceWidth}
                  y=${verticalOffset}
                  filter=${label ? "url(#green)" : "url(#red)"}
                >
                  ${svg`[label: ${label}]`}
                </text>
              `
            )
          )
          const renderedLines = (
            outSet.size > 0
              ? (
                Array.from(outSet).map(
                  (idx, j) => {
                    const x1 = tokenOffsets[idx] + (tokenWidths[idx] / 2)
                    const y1 = verticalOffset + (0.5 * pad)
                    const x2 = tokenOffsets[idx] + (tokenWidths[idx] / 2)
                    const y2 = y1 + visHeight + (3 * pad)
                    // clang-format off
                    return svg`
                      <line x1=${x1} y1=${y1} x2=${x2} y2=${y2}
                        stroke="${getBrandColor('cyea', '600').color}"
                        stroke-width=2 marker-end="url(#arrow)"
                      >
                      </line>
                      <text x=${x1 - 50} y=${0.5 * y1 + 0.5 * y2} style="font-size: 80%; letter-spacing: 1px; stroke: teal;">
                        WordSwapEmbedding{${idx}}{${idx}}
                      </text>
                    `
                    // clang-format on
                  }
                )
              ) : []
          )
          return svg`${
            Array.from(renderedTokens).concat(renderedLines)
          }`
        }
      }
      tokenizedTexts.push(tokenizedText)
      prevTokenizedText = tokenizedText
    }

    traceWidth += 100
    traceHeight = fontSize + traceHeight + fontSize

    // clang-format off
    return html`
      <div class="tx-prov-trace">
        <span style="font-size: 0.5rem; color: darkgrey">
          trace ${1+sno} (out of ${this.txProvTraces.length})
        </span>
        <ul class="trace-meta">
          <li>
            Text id — ${tokenizedTexts[0].textId}
          </li>
          ${
            null
            /*
              <li>
                Tx info — p l a c e h o l d e r
              </li>
              <li>
                Attack outcome —
                  <span style="font-weight: bolder; color: ${tokenizedTexts[0].label == tokenizedTexts[tokenizedTexts.length-1].label ? "red" : "green"};">
                    ${tokenizedTexts[0].label == tokenizedTexts[tokenizedTexts.length-1].label ? "Fail" : "Success" }
                  </span>
              </li>
            */
          }
        </ul>
        ${svg`
          <svg width=${traceWidth} height=${traceHeight} font-family="${fontFamily}" font-size="${fontSize}px">
            <defs>
              <filter x="0" y="0" width="1" height="1" id="yellow">
                <feFlood flood-color="yellow" result="bg" />
                <feMerge>
                  <feMergeNode in="bg"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <filter x="0" y="0" width="1" height="1" id="green">
                <feFlood flood-color="lightgreen" result="bg" />
                <feMerge>
                  <feMergeNode in="bg"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <filter x="0" y="0" width="1" height="1" id="red">
                <feFlood flood-color="tomato" result="bg" />
                <feMerge>
                  <feMergeNode in="bg"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <marker id="arrow" viewBox="0 -5 10 10" refX="5" refY="0" markerWidth="4" markerHeight="4" orient="auto">
                <path class="cool" d="M0,-5L10,0L0,5" class="arrowHead"></path>
              </marker>
            </defs>
            ${
              tokenizedTexts.map(text => text.render())
            }
          </svg>
        `}
      </div>
    `
    // clang-format on
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
    return html`
      <div class="module-container">
        <div style="margin: 10px;">
          <select class="dropdown" @change=${(e: Event) => this.onChangeSelectionType(e)}>
            ${this.selectionType == "default"
              ? html`<option value="default" selected>default</option>`
              : html`<option value="default">default</option>`
            }
            ${this.selectionType == "high_Q"
              ? html`<option value="high_Q" selected>👍 high quality</option>`
              : html`<option value="high_Q">👍 high quality</option>`
            }
            ${this.selectionType == "low_Q"
              ? html`<option value="low_Q" selected>👎 low quality</option>`
              : html`<option value="low_Q">👎 low quality</option>`
            }
          </select>
          <span class="dropdown-label"> <-- selection type </span>
        </div>
        <div class="module-results-area padded-container" style="margin-top: 10px;">
          ${this.txProvTraces.map((trace, sno) => this.renderTrace(trace, sno))}
        </div>
      </div>
    `
    // clang-format on
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'tx-feature-provenance-module': TxFeatureProvenanceModule
  }
}
