/* Copyright 2019 Banco Santander S.A.
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

import crypto from 'crypto';

const CYPHERTYPE = 'aes-256-gcm';
const MESSAGE_ENCODING = 'base64';
const OUT_ENCODING = 'utf8';
const TAG_OFFSET = 16;

export default {

    decipherOutData(key, iv, tagAndMessage) {

        const keyBuff = Buffer.from(new Uint8Array(key));
        const ivBuff = Buffer.from(new Uint8Array(iv));

        const tagAndMessageBuff = Buffer.from(tagAndMessage, MESSAGE_ENCODING);
        let messageBuff = Buffer.alloc(tagAndMessageBuff.length - TAG_OFFSET);
        tagAndMessageBuff.copy(messageBuff, 0, 0);
        let tagBuff = Buffer.alloc(TAG_OFFSET);
        tagAndMessageBuff.copy(tagBuff, 0, tagAndMessageBuff.length - TAG_OFFSET);

        const decipher = crypto.createDecipheriv(CYPHERTYPE, keyBuff, ivBuff);
        decipher.setAuthTag(tagBuff);
        let decrypted = decipher.update(messageBuff, OUT_ENCODING);
        decrypted += decipher.final(OUT_ENCODING);
        return decrypted;
    },

    processWorkOrderResult(message) {
        // Countries loaded: PL,ES,
        let resultArray = new Array(3);
        const [header, payload] = message.split(':');
        if (header === "Countries loaded") {
            let countriesArray = payload.split(',');
            countriesArray = countriesArray.map( el => el.trim());
            resultArray[0] = countriesArray.find( el => el === 'ES');
            resultArray[1] = countriesArray.find( el => el === 'PL');
            resultArray[2] = countriesArray.find( el => el === 'UK');
            return resultArray;
        }

        else {
            return [true,true,true];
        }

    },

    processListOfSuspects(message) {
        // Suspects found: {Hugo Zyla, Ester Ramos, Demario Goodwin} {Emil Lis, Sabryna Cole, Francisca Valdez}
        let resultArray = new Array();
        const [header, payload] = message.split(':');
        if (header === "Do not trust these people") {
            let resultArray = payload.split(';');
            return resultArray;
        }

        else {
            return [];
        }
    }
}
