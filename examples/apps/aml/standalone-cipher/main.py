#!/usr/bin/env python

# Copyright 2019 Banco Santander S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pandas as pd
import json
import uuid

import worker
import signature
import signingAlgorithm
import encryptionAlg

users = []
transactions = []
country = ""
numberUsers = 0
numberTransactions = 0


class App():
    def __init__(self):
        global root
        global users
        global country
        global numberUsers
        global transactions
        global numberTransactions
        global preprocess

        global e0, e1, e2, e4, e5, e7

        preprocess = ""

        root = Tk()
        root.geometry('700x520')
        root.configure(bg='white')
        root.title('AML client')

        # Setting the countries we are using
        ttk.Label(
            root, text="Countries participating").grid(
                row=0, padx=(100, 10), pady=(30, 7))
        e0 = ttk.Entry(root)
        b0 = ttk.Button(root, text='Initialize', command=self.loadCountries)

        e0.grid(row=0, column=1, pady=(30, 7))
        b0.grid(row=0, column=2, pady=(30, 7))

        # Creating the jsons from CSVs

        ttk.Label(root, text="Users CSV").grid(
            row=1, padx=(100, 10), pady=(30, 4))
        ttk.Label(
            root, text="Transactions CSV").grid(
                row=2, padx=(100, 10), pady=(0, 7))

        e1 = ttk.Entry(root)
        e2 = ttk.Entry(root)

        b1 = ttk.Button(root, text='Select', command=self.selectUsers)
        b2 = ttk.Button(root, text='Select', command=self.selectTransactions)
        b3 = ttk.Button(root, text='Create Json from CSVs',
                        command=self.createJsonFile)

        e1.grid(row=1, column=1, pady=(30, 4))
        e2.grid(row=2, column=1, pady=(0, 7))
        b1.grid(row=1, column=2, pady=(30, 4))
        b2.grid(row=2, column=2, pady=(0, 7))
        b3.grid(row=3, column=1)

        # Cont

        # Initializing encryption information
        ttk.Label(
            root, text="Worker info").grid(
                row=4, padx=(100, 10), pady=(30, 4))
        ttk.Label(
            root, text="EC private key").grid(
                row=5, padx=(100, 10), pady=(0, 7))

        e4 = ttk.Entry(root)
        e5 = ttk.Entry(root)

        b4 = ttk.Button(root, text='Select', command=self.selectWorkerObj)
        b5 = ttk.Button(root, text='Select', command=self.selecECPrivK)
        b6 = ttk.Button(root, text='Init cipher info',
                        command=self.initCipherInfo)

        e4.grid(row=4, column=1, pady=(30, 4))
        e5.grid(row=5, column=1, pady=(0, 7))
        b4.grid(row=4, column=2, pady=(30, 4))
        b5.grid(row=5, column=2, pady=(0, 7))
        b6.grid(row=6, column=1)

        # Encrypt JSON
        ttk.Label(
            root, text="Workload's JSON").grid(
                row=7, padx=(100, 10), pady=(30, 4))
        e7 = ttk.Entry(root)
        b7 = ttk.Button(root, text='Select', command=self.selectWorkloadJson)
        b8 = ttk.Button(
            root, text="Encrypt Workload's JSON",
            command=self.encryptJsonInData)

        e7.grid(row=7, column=1, pady=(30, 4))
        b7.grid(row=7, column=2, pady=(30, 4))
        b8.grid(row=8, column=1)

        # Logo
        img_logo = ImageTk.PhotoImage(Image.open(
            "./images/santander_logo.png"))
        panel_logo = Label(root, image=img_logo)
        panel_logo.grid(row=10, column=1, sticky=S, pady=(40, 0))

        root.mainloop()

    def loadCountries(self):
        global preprocess

        countries = e0.get()
        preprocess = countries.replace(",", "_")

    def selectUsers(self):
        global users_filename
        global e1

        users_filename = askopenfilename()

        e1.delete(0, END)
        e1.insert(0, users_filename.rsplit('/', 1)[-1])

    def selectTransactions(self):
        global transactions_filename
        global e2

        transactions_filename = askopenfilename()

        e2.delete(0, END)
        e2.insert(0, transactions_filename.rsplit('/', 1)[-1])

    def createJsonFile(self):
        global preprocess
        global users_filename, transactions_filename
        global save_json_filename

        save_json_filename = asksaveasfilename()

        users = pd.read_csv(users_filename)
        country = users['userId'][0][0:2]
        numberUsers = len(users)

        transactions = pd.read_csv(transactions_filename)
        numberTransactions = len(transactions)

        index = 0

        base_json_file = open("./json_building_blocks/base.json", "r")
        inData_json_file = open("./json_building_blocks/inData.json", "r")
        output_json_file = open(save_json_filename, "w")

        base_json_str = base_json_file.read()
        inData_json_str = inData_json_file.read()

        base_json = json.loads(base_json_str)
        inData_json = json.loads(inData_json_str)

        inData_str = "["

        if preprocess != "":
            inData_json_aux = inData_json
            inData_json_aux["index"] = index
            index += 1

            inData_aux = (
                preprocess + "|" + (
                    country + "," + str(numberUsers)
                    + "," + str(numberTransactions)))
        for i in range(0, numberUsers):
            inData_aux = (
                inData_aux + "|" + users['userId'][i] + "," + users['name'][i])
        for j in range(0, numberTransactions):
            inData_aux = (
                inData_aux + "|" + transactions['from'][j]
                + "," + transactions['to'][j]
                + "," + str(transactions['amount'][j])
                + "," + transactions['currency'][j]
                + "," + transactions['date'][j])

        inData_json_aux["data"] = inData_aux

        inData_str = inData_str + json.dumps(inData_json_aux) + "\n]"

        inData_full_json = json.loads(inData_str)

        workOrderId = "0x" + uuid.uuid4().hex[:16].upper()
        base_json["params"]["workOrderId"] = workOrderId
        base_json["params"]["inData"] = inData_full_json

        workloadId = base_json["params"]["workloadId"]
        workloadIdHex = workloadId.encode("UTF-8").hex()
        base_json["params"]["workloadId"] = workloadIdHex

        resultString = json.dumps(base_json)

        output_json_file.write(resultString)

        output_json_file.close()
        base_json_file.close()
        inData_json_file.close()

    def selectWorkerObj(self):
        global workerObj_filename
        global e4

        workerObj_filename = askopenfilename()
        e4.delete(0, END)
        e4.insert(0, workerObj_filename.rsplit('/', 1)[-1])

    def selecECPrivK(self):
        global ECPrivk_filename
        global e5

        ECPrivk_filename = askopenfilename()
        e5.delete(0, END)
        e5.insert(0, ECPrivk_filename.rsplit('/', 1)[-1])

    def initCipherInfo(self):
        global workerObj_filename, ECPrivk_filename
        global EC_key
        global worker_obj

        ec_file = open(ECPrivk_filename, "r")
        EC_key = ec_file.read()

        worker_file = open(workerObj_filename, "r")
        worker_str = worker_file.read().rstrip('\n')
        worker_json = json.loads(worker_str)
        worker_obj = worker.SGXWorkerDetails()
        worker_obj.load_worker(worker_json)

        worker_file.close()
        ec_file.close()

    def selectWorkloadJson(self):
        global WorkloadJson_filename
        global e7
        global save_json_filename

        WorkloadJson_filename = askopenfilename(
            initialdir="/".join(save_json_filename.split("/")[:-1]))
        e7.delete(0, END)
        e7.insert(0, WorkloadJson_filename.rsplit('/', 1)[-1])

    def encryptJsonInData(self):
        global EC_key
        global WorkloadJson_filename
        global worker_obj

        enc_json_file = asksaveasfilename()
        save_key_file = asksaveasfilename()

        json_file = open(WorkloadJson_filename, "r")
        workload_str = json_file.read()
        workload_json = json.loads(workload_str)
        workload_json["params"]["workerId"] = worker_obj.worker_id

        workload_str = json.dumps(workload_json)

        sig_obj = signature.ClientSignature()

        signing_key = signingAlgorithm.signAlgorithm()
        signing_key.loadKey(EC_key)

        session_iv = sig_obj.generate_sessioniv()

        enc_obj = encryptionAlg.encAlgorithm()
        session_key = enc_obj.generateKey()

        enc_session_key = sig_obj.generate_encrypted_key(
            session_key, worker_obj.encryption_key)

        request_json = sig_obj.generate_client_signature(
            workload_str, worker_obj, signing_key, session_key, session_iv,
            enc_session_key)

        enc_json_file = open(enc_json_file, "w")
        enc_json_file.write(request_json)

        enc_session_json = '{"key": ' + str(list(session_key)) + ',"iv": ' \
            + str(list(session_iv)) + '}'

        enc_session_key_file = open(save_key_file, "w")
        enc_session_key_file.write(enc_session_json)

        json_file.close()
        enc_json_file.close()
        enc_session_key_file.close()


def main():
    App()

    return 0


if __name__ == '__main__':
    main()
