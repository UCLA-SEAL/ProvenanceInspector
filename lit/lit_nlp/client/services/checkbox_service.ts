import { action, computed, observable, reaction } from "mobx";

import { LitService } from "./lit_service";
import { AppState } from "./state_service";

export class CheckboxService extends LitService {

  constructor(private readonly appState: AppState) {
    super()
  }

}