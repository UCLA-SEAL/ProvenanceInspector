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
import '@material/mwc-switch';
import '../elements/checkbox';
import '../elements/popup_container';

import {html} from 'lit';
import {customElement, query, property} from 'lit/decorators';
import {classMap} from 'lit/directives/class-map';
import {styleMap} from 'lit/directives/style-map';
import {action, computed, observable} from 'mobx';
import * as papa from 'papaparse';

import {PopupContainer} from '../elements/popup_container';

import {app} from '../core/app';
import {LitModule} from '../core/lit_module';
import {ColumnHeader, DataTable, TableData} from '../elements/table';
import {BooleanLitType, LitType, LitTypeWithVocab, TextSegment} from '../lib/lit_types';
import {styles as sharedStyles} from '../lib/shared_styles.css';
import {formatForDisplay, IndexedInput, ModelInfoMap, Spec} from '../lib/types';
import {compareArrays} from '../lib/utils';
import {DataService, FocusService, QualityMarkService, FilterBySimilarDataService, SelectionService, SliceService} from '../services/services';
import {STARRED_SLICE_NAME} from '../services/slice_service';

import {styles} from './data_table_module.css';

/**
 * A LIT module showing a table containing the InputData examples. Allows the
 * user to sort, filter, and select examples.
 */
@customElement('data-inspection-table-module')
export class DataInspectionTableModule extends LitModule {
  static override title = 'Data Inpsection Table (of augmented data)';
  static override template =
      (model: string, selectionServiceIndex: number, shouldReact: number) => html`
      <data-inspection-table-module model=${model} .shouldReact=${shouldReact}
        selectionServiceIndex=${selectionServiceIndex}>
      </data-inspection-table-module>`;
  static override numCols = 4;
  static override get styles() {
    return [sharedStyles, styles];
  }

  static override duplicateForModelComparison = false;

  protected showControls = true;

  private readonly focusService = app.getService(FocusService);
  private readonly qualityMarkService = app.getService(QualityMarkService);
  private readonly filterBySimilarDataService = app.getService(FilterBySimilarDataService);
  private readonly dataService = app.getService(DataService);
  private readonly sliceService = app.getService(SliceService);
  private readonly referenceSelectionService =
      app.getService(SelectionService, 'pinned');

  @observable columnVisibility = new Map<string, boolean>();
  @observable searchText = '';

  @property({type: String}) downloadFilename: string = 'data_inspector.csv';

  // Module options / configuration state
  @observable private onlyShowGenerated: boolean = false;
  @observable private onlyShowSelected: boolean = false;
  @observable private showSimilar: boolean = false;

  // Child components
  @query('lit-data-table') private readonly table?: DataTable;

  @computed
  get dataSpec(): Spec {
    return this.appState.currentDatasetSpec;
  }

  // Column names from the current data for the data table.
  @computed
  get keys(): ColumnHeader[] {

    return [ {name: 'Sentence'}, {name: 'label'}]

  }

  // Filtered keys that hide ones tagged as not to be shown by default in the
  // data table. The filtered ones can still be enabled through the "Columns"
  // selector dropdown.
  @computed
  get defaultKeys(): ColumnHeader[] {
    return this.keys.filter(feat => {
      const col = this.dataService.getColumnInfo(feat.name);
      if (col == null) {
        return true;
      }
      return col.dataType.show_in_data_table;
    });
  }

  // All columns to be available by default in the data table.
  @computed
  get defaultColumns(): ColumnHeader[] {
    return [{name:'idx'}, {name: 'Sentence'}, {name: 'label'}];
  }

  @computed
  get pinnedInputData(): IndexedInput[] {
    return this.appState.currentInputData.filter((inputData) => {
      return this.referenceSelectionService.primarySelectedId === inputData.id;
    });
  }

  @computed
  get filteredData(): IndexedInput[] {
    // Baseline data is either the selection, the whole dataset, or filtered to be similar to the `filteredBySimilarData` data marked by the user
    const data = 
      // this.onlyShowSelected ?
        // this.selectionService.selectedInputData :
        this.appState.currentInputData;
 
    
    return data;
  }

  private extractProvenance(data: IndexedInput[]) {
    var transformIndices = [];
    var featureIndices = [];

    var dataIndexToData = data.reduce(function(map, obj) {
        map[obj.data['idx']] = obj;
        return map;
      }, {});

    Array.from(this.qualityMarkService.highQualityIndices)
    .map(index => dataIndexToData[index])
    .forEach(function (element) {
      // element['transforms'].split(' ')
      // console.log(element.data['transforms']);  
      element.data['transforms'].substr(1, element.data['transforms'].length -1).split(' ').map(strElement => parseInt(strElement))
        .map((element, index) => {
          if (element === 1) {
            return index;
          }
        })
        .filter(element => element !== undefined)
        .forEach(element => transformIndices = transformIndices.concat(element));

      element.data['features'].substr(1, element.data['features'].length -1).split(' ').map(strElement => parseInt(strElement))
        .map((element, index) => {
          if (element === 1) {
            return index;
          }
        })
        .filter(element => element !== undefined)
        .forEach(element => featureIndices = featureIndices.concat(element));
    });
    return { transformIndices, featureIndices };
  }

  @computed
  get sortedData(): IndexedInput[] {
    // TODO(lit-dev): pre-compute the index chains for each point, since
    // this might get slow if we have a lot of counterfactuals.
    if (this.showSimilar) {
          // first, if showSimilar, then compute overlap in transforms and features to the labelled data
          var { transformIndices, featureIndices } = this.extractProvenance(this.appState.currentInputData);
          console.log('[sortedData]')
          console.log(transformIndices);
          // enumerate over data
          const sortedData = this.filteredData.slice().sort(
            (a, b) => {
              // compute overlap in transforms and features
              const aTransforms = a.data['transforms'].substr(1, a.data['transforms'].length -1).split(' ').map(strElement => parseInt(strElement));
              const bTransforms = b.data['transforms'].substr(1, b.data['transforms'].length -1).split(' ').map(strElement => parseInt(strElement));

              const aFeatures = a.data['features'].substr(1, a.data['features'].length -1).split(' ').map(strElement => parseInt(strElement));
              const bFeatures = b.data['features'].substr(1, b.data['features'].length -1).split(' ').map(strElement => parseInt(strElement));
              
              const aTransformsOverlap = this.computeOverlap(aTransforms, transformIndices);
              const bTransformsOverlap = this.computeOverlap(bTransforms, transformIndices);

              const aFeaturesOverlap = this.computeOverlap(aFeatures, featureIndices);
              const bFeaturesOverlap = this.computeOverlap(bFeatures, featureIndices);
              
              // sort by overlap in transforms
              if (aTransformsOverlap.length + aFeaturesOverlap.length > bTransformsOverlap.length + bFeaturesOverlap.length) {
                return -1;
              }
              if (aTransformsOverlap.length + aFeaturesOverlap.length < bTransformsOverlap.length + bFeaturesOverlap.length) {
                return 1;
              }

              return 0;
            }
          );
          console.log('sortedData');
          console.log(sortedData);
          return sortedData;

    } else {
      return this.filteredData.slice().sort(
          (a, b) => {

        
            return compareArrays(
              this.reversedAncestorIndices(a), this.reversedAncestorIndices(b)
            )
          }
      );
    }
  }

  private computeOverlap(features, featureIndices: any[]) {
    return features.map((element, index) => {
      if (element === 1) {
        return index;
      }
    })
      .filter(element => element !== undefined)
      .filter(element => featureIndices.includes(element));
  }

  @computed
  get dataEntries(): Array<Array<string|number>> {
    return this.sortedData.map((d) => {
      const index = this.appState.indicesById.get(d.id);
      if (index == null) return [];

      const dataEntries =
          this.keys
          // .filter(k => this.columnVisibility.get(k.name))
              .map(
                  k => formatForDisplay(
                      this.dataService.getVal(d.id, k.name),
                      this.dataSpec[k.name]));
      return dataEntries;
    });
  }

  @computed
  get selectedRowIndices(): number[] {
    return this.sortedData
        .map((ex, i) => this.selectionService.isIdSelected(ex.id) ? i : -1)
        .filter(i => i !== -1);
  }

  @computed
  get tableDataIds(): string[] {
    return this.sortedData.map(d => d.id);
  }

  private indexOfId(id: string|null) {
    return id != null ? this.tableDataIds.indexOf(id) : -1;
  }

  @computed
  get primarySelectedIndex(): number {
    return this.indexOfId(this.selectionService.primarySelectedId);
  }

  @computed
  get referenceSelectedIndex(): number {
    if (this.appState.compareExamplesEnabled) {
      return this.indexOfId(this.referenceSelectionService.primarySelectedId);
    }
    return -1;
  }

  @computed
  get starredIndices(): number[] {
    const starredIds = this.sliceService.getSliceByName(STARRED_SLICE_NAME);
    if (starredIds) {
      return starredIds.map(sid => this.indexOfId(sid));
    }
    return [];
  }

  @computed
  get focusedIndex(): number {
    // Set focused index if a datapoint is focused according to the focus
    // service. If the focusData is null then nothing is focused. If focusData
    // contains a value in the "io" field then the focus is on a subfield of
    // a datapoint, as opposed to a datapoint itself.
    const focusData = this.focusService.focusData;
    return focusData == null || focusData.io != null ?
        -1 :
        this.indexOfId(focusData.datapointId);
  }

  /**
   * Recursively follow parent pointers and list their numerical indices.
   * Returns a list with the current index last, e.g.
   * [grandparent, parent, child]
   */
  private reversedAncestorIndices(d: IndexedInput): number[] {
    const ancestorIds = this.appState.getAncestry(d.id);
    // Convert to indices and return in reverse order.
    return ancestorIds.map((id) => this.appState.indicesById.get(id)!)
        .reverse();
  }

  private isStarred(id: string|null): boolean {
    return (id !== null) && this.sliceService.isInSlice(STARRED_SLICE_NAME, id);
  }

  private toggleStarred(id: string|null) {
    if (id == null) return;
    if (this.isStarred(id)) {
      this.sliceService.removeIdsFromSlice(STARRED_SLICE_NAME, [id]);
    } else {
      this.sliceService.addIdsToSlice(STARRED_SLICE_NAME, [id]);
    }
  }


  @computed
  get numberOfHighQualityLabels(): number {
    var highQualityInstances = new Set();

    this.qualityMarkService.highQualityIndices.forEach(highQualityIndex => highQualityInstances.add(highQualityIndex));

    var totalDatapointsMatchingTransforms = 0;
    this.qualityMarkService.highQualityTransforms.forEach(transformIndex => {
      var matchingDatapoints = this.filterBySimilarDataService.datapointsWithTransforms.get(transformIndex);

      totalDatapointsMatchingTransforms += matchingDatapoints.length;
      matchingDatapoints.forEach(matchingDatapoint => 
        highQualityInstances.add(matchingDatapoint['idx'])
      )
      
    });

  
    var totalDatapointsMatchingFeatures = 0;
    this.qualityMarkService.highQualityFeatures.forEach(featureIndex => {
      var matchingDatapoints = this.filterBySimilarDataService.dataSliceOfFeatureType.get(featureIndex);

      totalDatapointsMatchingFeatures += matchingDatapoints.length;
      matchingDatapoints.forEach(matchingDatapoint => 
        highQualityInstances.add(matchingDatapoint['idx'])
      )
    });

    // return this.qualityMarkService.highQualityIndices.size + totalDatapointsMatchingTransforms + totalDatapointsMatchingFeatures;

    return highQualityInstances.size;
  }

  // TODO(lit-dev): figure out why this updates so many times;
  // it gets run _four_ times every time a new datapoint is added.
  @computed
  get tableData(): TableData[] {
    return this.dataEntries.map((dataEntry, i) => {
      const d = this.sortedData[i];
      const index = this.appState.indicesById.get(d.id);
      if (index == null) return [];

      const pinClick = (event: Event) => {
        const pinnedId = this.appState.compareExamplesEnabled ?
            this.referenceSelectionService.primarySelectedId :
            null;
        if (pinnedId === d.id) {
          this.appState.compareExamplesEnabled = false;
          this.referenceSelectionService.selectIds([]);
        } else {
          this.appState.compareExamplesEnabled = true;
          this.referenceSelectionService.selectIds([d.id]);
        }
        event.stopPropagation();
      };

      const starClick = (event: Event) => {
        this.toggleStarred(d.id);
        event.stopPropagation();
        event.preventDefault();
      };

      // Provide a template function for the 'index' column so that the
      // rendering can be based on the selection/hover state of the datapoint
      // represented by the row.
      function templateFn(
          isSelected: boolean, isPrimarySelection: boolean,
          isReferenceSelection: boolean, isFocused: boolean,
          isStarred: boolean) {
        const indexHolderDivStyle = styleMap({
          'display': 'flex',
          'justify-content': 'space-between',
          'width': '100%'
        });
        const indexButtonsDivStyle = styleMap({
          'display': 'flex',
          'flex-direction': 'row',
          'column-gap': '8px',
        });
        const indexDivStyle = styleMap({
          'text-align': 'right',
          'flex': '1',
        });
        // Render the action button next to the index if datapoint is selected,
        // hovered, or active (pinned, starred).
        function renderActionButtons() {
          function getActionStyle(isActive: boolean) {
            return styleMap({
              'visibility': isPrimarySelection || isFocused || isActive ?
                  'default' :
                  'hidden',
            });
          }

          function getActionClass(isActive: boolean) {
            return classMap({
              'icon-button': true,
              'cyea': true,
              'mdi-outlined': !isActive,
            });
          }

          if (isPrimarySelection || isFocused || isReferenceSelection ||
              isStarred) {
            return html`
              <mwc-icon style="${getActionStyle(isReferenceSelection)}"
                class="${getActionClass(isReferenceSelection)}"
                @click=${pinClick}
                title=${`${isReferenceSelection ? 'Pin' : 'Unpin'} datapoint`}>
                push_pin
              </mwc-icon>
              <mwc-icon style="${getActionStyle(isStarred)}" @click=${starClick}
                class="${getActionClass(isStarred)}"
                title=${isStarred ? 'Remove from starred slice' :
                                    'Add to starred slice'}>
                ${isStarred ? 'star' : 'star_border'}
              </mwc-icon>`;
          }
          return null;
        }

        return html`
            <div style="${indexHolderDivStyle}">
              <div style=${indexButtonsDivStyle}>
               ${renderActionButtons()}
              </div>
              <div style="${indexDivStyle}">${index}</div>
            </div>`;
      }

      const indexEntry = {template: templateFn, value: index};
      return [indexEntry, ...dataEntry];
    });
  }

  override firstUpdated() {
    const updateColsChange = () =>
        [this.appState.currentModels, this.appState.currentDataset, this.keys];
    this.reactImmediately(updateColsChange, () => {
      // this.updateColumns();
    });
  }

  private updateColumns() {
    const columnVisibility = new Map<string, boolean>();

    // Add default columns to the map of column names.
    for (const column of this.defaultColumns) {
      columnVisibility.set(
          column.name,
          this.defaultKeys.includes(column) || column.name === 'index');
    }
    this.columnVisibility = columnVisibility;
  }

  private datasetIndexToRowIndex(inputIndex: number): number {
    const indexedInput = this.appState.currentInputData[inputIndex];
    if (indexedInput == null) return -1;
    return this.sortedData.findIndex(d => d.id === indexedInput.id);
  }

  /**
   * Table callbacks receive indices corresponding to the rows of
   * this.tableData, which matches this.sortedData.
   * We need to map those back to global ids for selection purposes.
   */
  getIdFromTableIndex(tableIndex: number) {
    return this.sortedData[tableIndex]?.id;
  }

  onSelect(tableDataIndices: number[]) {
    const ids = tableDataIndices.map(i => this.getIdFromTableIndex(i))
                    .filter(id => id != null);
    this.selectionService.selectIds(ids, this);
  }

  onPrimarySelect(tableIndex: number) {
    const id = this.getIdFromTableIndex(tableIndex);
    this.selectionService.setPrimarySelection(id, this);
  }

  onFilterSimilar() {
    this.showSimilar = !this.showSimilar;
  }

  onHover(tableIndex: number|null) {
    if (tableIndex == null) {
      this.focusService.clearFocus();
    } else {
      const id = this.getIdFromTableIndex(tableIndex);
      this.focusService.setFocusedDatapoint(id);
    }
  }

  onToggleHighQuality(tableIndex: number, status: boolean) {
    const data = this.appState.currentInputData;

    const dataIndex = data[tableIndex].data['idx'];
    
    if (status) {
      this.qualityMarkService.markHighQuality(dataIndex);

      this.filterBySimilarDataService.initializeTransformsToDataIfNotExist(data);
      this.filterBySimilarDataService.initializeFeaturesToDataIfNotExist(data);

      var { transformIndices, featureIndices } = this.extractProvenance(data);
      this.filterBySimilarDataService.setCommonTransforms(transformIndices);
      this.filterBySimilarDataService.setCommonFeatures(featureIndices);
 
      
    } else {
      this.qualityMarkService.unmarkHighQuality(dataIndex);

      var { transformIndices, featureIndices } = this.extractProvenance(data);
      this.filterBySimilarDataService.setCommonTransforms(transformIndices);
      this.filterBySimilarDataService.setCommonFeatures(featureIndices);

      // reset the high quality transforms and features as well
      var highQTransformsToUnmark = [];
      this.qualityMarkService.highQualityTransforms.forEach(transform => {
        if (!transformIndices.includes(transform)) {
          highQTransformsToUnmark.push(transform);
        }
      });
      highQTransformsToUnmark.forEach(transform => {
        this.qualityMarkService.unmarkHighQualityTransforms(transform);
      });

      var highQFeaturesToUnmark = [];
      this.qualityMarkService.highQualityFeatures.forEach(feature => {
        if (!featureIndices.includes(feature)) {
          highQFeaturesToUnmark.push(feature);
        }
      });
      highQFeaturesToUnmark.forEach(feature => {
        this.qualityMarkService.unmarkHighQualityFeatures(feature);
      });
      

    }

    console.log('high quality!');
  }

  onToggleLowQuality(tableIndex: number, status: boolean) {
    if (status) {
      this.qualityMarkService.markLowQuality(tableIndex);
    } else {
      this.qualityMarkService.unmarkLowQuality(tableIndex);
    }
    console.log('low quality!');
  }

  onToggleFilterBySimilarData(tableIndex: number, status: boolean) {
    if (status) {
      this.filterBySimilarDataService.selectDatapoint(tableIndex);
    } else {
      this.filterBySimilarDataService.unselectDatapoint(tableIndex);
    }
    console.log('onToggleFilterBySimilarData!!');
  }

  renderDropdownItem(key: string) {
    const checked = this.columnVisibility.get(key);
    if (checked == null) return;

    const toggleChecked = () => {
      this.columnVisibility.set(key, !checked);
    };

    // clang-format off
    return html`
      <div>
        <lit-checkbox class='column-select'
         label=${key} ?checked=${checked}
                      @change=${toggleChecked}>
        </lit-checkbox>
      </div>
    `;
    // clang-format on
  }

  renderColumnDropdown() {
    const names = [...this.columnVisibility.keys()].filter(c => c !== 'index');

    // clang-format off
    return html`
      <popup-container class='column-dropdown-container'>
        <button class='hairline-button' slot='toggle-anchor-closed'>
          <span class='material-icon-outlined'>view_column</span>
          &nbsp;Columns&nbsp;
          <span class='material-icon'>expand_more</span>
        </button>
        <button class='hairline-button' slot='toggle-anchor-open'>
          <span class='material-icon-outlined'>view_column</span>
          &nbsp;Columns&nbsp;
          <span class='material-icon'>expand_less</span>
        </button>
        <div class='column-dropdown'>
          ${names.map(key => this.renderDropdownItem(key))}
        </div>
      </popup-container>
    `;
    // clang-format on
  }

  renderControls() {
    const downloadCSV = () => {
      const csvContent ="";
      const blob = new Blob([csvContent], {type: 'text/csv'});
      const a = window.document.createElement('a');
      a.href = window.URL.createObjectURL(blob);
      a.download = "data_inspector_labels.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
    };

    const onClickResetView = () => {this.table?.resetView();};

    const onClickSelectFiltered = () => {
      this.onSelect(this.table!.getVisibleDataIdxs());
    };

    const onClickFilterSimilar = () => {
      this.onFilterSimilar();
    };

    // clang-format off
    return html`
      <div style="display:none">${this.renderColumnDropdown()}</div>
      <div class="toggles-row">
        <div class="number-of-interactions">

          <p> ${this.numberOfHighQualityLabels} already inspected to be high quality</p>
          <div class='download-popup-controls'>
            <label style="display:none;" for="filename">Filename</label>
            <input style="display:none;"  type="text" name="filename" >
            <button style="display:none;"  class='filled-button nowrap' @click=${downloadCSV}>
              Download labels
            </button>
          </div>
        </div>
 

      </div>
      <div id="toolbar-buttons">
        
 
      </div>
    `;
    // clang-format on
  }

  renderTable() {
    // const columnNames =
    //     this.defaultColumns.filter(col => this.columnVisibility.get(col.name));
    //   console.log(columnNames);
    const columnNames = this.defaultColumns;

    const shiftSelectStartRowIndex = this.datasetIndexToRowIndex(
        this.selectionService.shiftSelectionStartIndex);
    const shiftSelectEndRowIndex = this.datasetIndexToRowIndex(
        this.selectionService.shiftSelectionEndIndex);

    // clang-format off
    return html`
      <lit-data-table
        .data=${this.tableData}
        .columnNames=${columnNames}
        .selectedIndices=${this.selectedRowIndices}
        .primarySelectedIndex=${this.primarySelectedIndex}
        .referenceSelectedIndex=${this.referenceSelectedIndex}
        .starredIndices=${this.starredIndices}
        .focusedIndex=${this.focusedIndex}
        .highQualityIndices=${this.qualityMarkService.highQualityIndices}
        .lowQualityIndices=${this.qualityMarkService.lowQualityIndices}
        .filterBySimilarDataIndices=${this.filterBySimilarDataService.markedIndices}

        .onSelect=${(idxs: number[]) => { this.onSelect(idxs); }}
        .onPrimarySelect=${(i: number) => { this.onPrimarySelect(i); }}
        .onHover=${(i: number|null)=> { this.onHover(i); }}
        .onToggleHighQuality=${(index: number, status: boolean) => {this.onToggleHighQuality(index, status)}}
        .onToggleLowQuality=${(index: number, status: boolean) => {this.onToggleLowQuality(index, status)}}
        .onToggleFilterBySimilarData=${(index: number, status: boolean) => {this.onToggleFilterBySimilarData(index, status)}}
        searchEnabled
        selectionEnabled
        
        qualityMarkEnabled
        filterBySimilarDataEnabled

        shiftSelectionStartIndex=${shiftSelectStartRowIndex}
        shiftSelectionEndIndex=${shiftSelectEndRowIndex}
      ></lit-data-table>
    `;
    // clang-format on
  }

  renderExportControls() {


    const getQualityRows = () => {
      const highQualityInstances = [];

      const data = this.filteredData;
 
      this.qualityMarkService.highQualityIndices.forEach(function(highQualityIndex) {

        const datapoint = data[highQualityIndex];
        highQualityInstances.push( {
          'idx': datapoint.data['idx'],
          'text': datapoint.data['Sentence'],
          'label': datapoint.data['raw_label']
        })
      });

      // console.log('getQualityRows');

      return highQualityInstances;
    }

    const csvContent = function() {

      return papa.unparse(
        {fields: ['idx', 'text', 'label'], data: getQualityRows()},
        {newline: '\r\n'});

    }

    const downloadCSV = () => {
      const content = csvContent();       // this.getCSVContent();
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

    const updateFilename = (e: Event) => {
      // tslint:disable-next-line:no-any
      this.downloadFilename = (e as any).target.value as string;
    };

    function onEnter(e: KeyboardEvent) {
      if (e.key === 'Enter') downloadCSV();
    }

    // clang-format off
    return html`

      <popup-container class='download-popup'>
        <mwc-icon class='icon-button' slot='toggle-anchor'
          title="Download high quality data">
          file_download
        </mwc-icon>
        <div class='download-popup-controls'>
          <label for="filename">Filename</label>
          <input type="text" name="filename" value=${this.downloadFilename}
           @input=${updateFilename} @keydown=${onEnter}>
          <button class='filled-button nowrap' @click=${downloadCSV}>
            Download high quality data
          </button>
        </div>
      </popup-container>
    `;
    // clang-format on
  }

  override renderImpl() {
    // clang-format off
    return html`
      <div class='module-container'>
        ${this.showControls ? html`
          <div class='module-toolbar'>
            ${this.renderControls()}
          </div>
        ` : null}
        <div class='module-results-area'>
          ${this.renderTable()}
        </div>

        <div class="footer" style="margin-bottom:12px">
          ${this.renderExportControls()}
        </div>

      </div>
    `;
    // clang-format on
  }

  static override shouldDisplayModule(
      modelSpecs: ModelInfoMap, datasetSpec: Spec) {
    return true;
  }
}

/**
 * Simplified version of the above; omits toolbar controls.
 */


declare global {
  interface HTMLElementTagNameMap {
    'data-inspection-table-module': DataInspectionTableModule;
    
  }
}
