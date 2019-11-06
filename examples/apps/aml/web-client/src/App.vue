<!-- 
  Copyright 2019 Banco Santander S.A.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. 
-->

<template>
  <div id="app">
    <b-container>
      <div class="text-center m-4">
        <b-img :src="logo" fluid alt="Santander Logo"></b-img>
      </div>

      <h3 class="mt-3">Available workers</h3>

      <div class="text-center" v-if="workerList === null">
        <h4>Looking up Workers</h4>
        <b-spinner variant="danger" label="Loading..."></b-spinner>
      </div>
      <div v-else>
        <b-table :items="workerList" :fields="fields" class="mt-3" outlined>
          <template slot="show_details" slot-scope="row">
            <b-button
              size="sm"
              @click="requestDelete(row.item.Worker_ID_public_EC_key)"
              class="mr-2"
              variant="outline-primary"
            >Details</b-button>
          </template>
        </b-table>
      </div>

      <b-modal size="lg" title="Worker Details" ref="modal" @show="nullWorker" ok-only>
        <div class="text-center" v-if="currentWorker === null">
          <h4>Retrieving Worker</h4>
          <b-spinner variant="danger" label="Loading..."></b-spinner>
        </div>
        <div v-else class="m-4">
          <p>
            <b>Organization ID:</b>
            {{currentWorker.result.organizationId}}
          </p>
          <p>
            <b>Worker URI:</b>
            {{currentWorker.result.details.workOrderSyncUri}}
          </p>
          <p>
            <b>RSA Key:</b>
          </p>
          <p>{{currentWorker.result.details.workerTypeData.encryptionKey}}</p>

          <div class="text-center">
            <a :href="blobLink" download="worker_information.json">
              <b-button variant="outline-primary">Download Worker Information</b-button>
            </a>
          </div>
        </div>
      </b-modal>

      <hr />
      <h3 class="mt-3">Submit data to the worker</h3>

      <b-form>

        <b-form-file
          v-model="file"
          :state="Boolean(file)"
          placeholder="Select a ciphered work order..."
          drop-placeholder="Drop file here..."
          required
        ></b-form-file>
        <div class="my-3">Selected file: {{ file ? file.name : '' }}</div>
      </b-form>
      <b-button block variant="outline-primary" @click="submitWorkOrder">Submit work order</b-button>

      <hr />

      <h3 class="mt-3">Countries that have data submitted</h3>

      <b-alert
        variant="warning"
        dismissible
        fade
        :show="alertPendingError"
        @dismissed="alertPendingError=false"
      >{{messagePendingError}}</b-alert>

      <b-list-group>
        <b-list-group-item :variant="countriesLoaded[0] ? 'success' : 'light'">Spain</b-list-group-item>
        <b-list-group-item :variant="countriesLoaded[1] ? 'success' : 'light'">Poland</b-list-group-item>
        <b-list-group-item :variant="countriesLoaded[2] ? 'success' : 'light'">United Kingdom</b-list-group-item>
      </b-list-group>
      <b-form class="mt-4">
        <b-form-file
          v-model="decryptionKey"
          :state="Boolean(decryptionKey)"
          placeholder="Select the decryption key..."
          drop-placeholder="Drop file here..."
          required
        ></b-form-file>
        <div class="my-3">Selected file: {{ decryptionKey ? decryptionKey.name : '' }}</div>
      </b-form>
      <b-button block variant="outline-primary" class="my-4" @click="getWorkerOrderResult">Refresh</b-button>

      <hr />

      <div class="mb-4" v-if="listOfSuspects !== null">
        <h3 class="mt-3">List of suspects</h3>
        <b-list-group>
          <b-list-group-item v-for="suspect in listOfSuspects">{{ suspect }}</b-list-group-item>
        </b-list-group>
      </div>
    </b-container>
  </div>
</template>

<script>
import sgxService from "./services/sgx.service.js";
import cipherUtils from "./utils/cipher.utils.js";

export default {
  name: "app",
  components: {},
  data() {
    return {
      blob: null,
      blobLink: null,
      file: null,
      decryptionKey: null,
      countriesLoaded: [false, false, false],
      lastWorkOrderId: null,
      currentPK: "",
      currentWorker: null,
      fields: ["Worker_ID_public_EC_key", "show_details"],
      listOfSuspects: null,
      workerList: null,
      logo: require("./assets/logo.png"),

      alertPendingError: false,
      messagePendingError: "Last work order is being processed"
    };
  },
  methods: {
    submitWorkOrder() {
      if (this.file === null) {
        this.$swal({
          type: "info",
          title: "Select a ciphered Work Order"
        });
      } else {
        this.readJSONFromFile().then(parsedFile => {
          sgxService.submitWorkOrder(parsedFile).then(wo => {
            if (wo.error.code == 8) {
              this.$swal({
                type: "error",
                title: "Work order already exists"
              });
            } else if (wo.error.code == 5) {
              this.$swal({
                type: "success",
                title: "Your work order is being processed"
              });
            }
          });
        });
      }
    },

    getWorkerOrderResult() {
      this.readKeyFromFile().then(decipherKey => {
        sgxService.getWorkerOrderResult(this.lastWorkOrderId).then(wor => {
          if (wor.error) {
            this.alertPendingError = true;
          } else {
            const { data } = wor.result.outData[0];
            const receiptResult = cipherUtils.decipherOutData(
              decipherKey.key,
              decipherKey.iv,
              data
            );
            this.countriesLoaded = cipherUtils.processWorkOrderResult(
              receiptResult
            );
            localStorage.countriesLoaded = JSON.stringify(this.countriesLoaded);
            if (this.countriesLoaded.reduce((acum, el) => el && acum)) {
              this.listOfSuspects = cipherUtils.processListOfSuspects(
                receiptResult
              );
            }
          }
        });
      });
    },

    readJSONFromFile() {
      return new Promise(resolve => {
        let reader = new FileReader();
        reader.onload = function(e) {
          const fileParsed = JSON.parse(e.target.result);
          resolve(fileParsed);
          this.lastWorkOrderId = fileParsed.params.workOrderId;
        }.bind(this);
        reader.readAsText(this.file);
      });
    },

    readKeyFromFile() {
      return new Promise(resolve => {
        let reader = new FileReader();
        reader.onload = function(e) {
          resolve(JSON.parse(e.target.result));
        }.bind(this);
        reader.readAsText(this.decryptionKey);
      });
    },

    nullWorker() {
      this.currentWorker = null;
    },

    requestDelete(workerPK) {
      this.currentPK = workerPK;
      sgxService.getWorkerDetails(workerPK).then(wrk => {
        this.currentWorker = wrk;
        this.blob = new Blob(
          [JSON.stringify(this.currentWorker)],
          { type: "text/plain;charset=utf-8" }
        );
        this.blobLink = URL.createObjectURL(this.blob);
      });
      this.$refs["modal"].show();
    }
  },
  mounted() {
    sgxService.getWorkerList().then(wl => (this.workerList = wl));
    if (localStorage.countriesLoaded === undefined) {
      localStorage.countriesLoaded = JSON.stringify([false, false, false]);
    }
    this.countriesLoaded = JSON.parse(localStorage.countriesLoaded);
  }
};
</script>

<style>
table, th, td {
  max-width: 800px;
  overflow: scroll;
}
</style>
