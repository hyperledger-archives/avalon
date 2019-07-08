package com.iexec.worker.result;

import com.iexec.worker.chain.CredentialsService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.sms.SmsService;
import com.iexec.worker.tee.scone.SconeEnclaveSignatureFile;

import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.assertj.core.api.Java6Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.util.Optional;

public class ResultServiceTests {

    private final String IEXEC_WORKER_TMP_FOLDER = "./src/test/resources/tmp/test-worker";

    @Mock private WorkerConfigurationService workerConfigurationService;
    @Mock private ResultRepoService resultRepoService;
    @Mock private CredentialsService credentialsService;
    @Mock private IexecHubService iexecHubService;
    @Mock private SmsService smsService;

    @InjectMocks
    private ResultService resultService;

    @Before
    public void init() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    public void shouldGetContentOfDeterminismFileSinceBytes32(){
        String chainTaskId = "bytes32";

        when(iexecHubService.isTeeTask(chainTaskId)).thenReturn(false);
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output/iexec_out");

        String hash = resultService.getTaskDeterminismHash(chainTaskId);
        // should be equal to the content of the file since it is a byte32
        assertThat(hash).isEqualTo("0xda9a34f3846cc4434eb31ad870aaf47c8a123225732db003c0c19f3c3f6faa01");
    }

    @Test
    public void shouldGetHashOfDeterminismFileSinceNotByte32(){
        String chainTaskId = "notBytes32";

        when(iexecHubService.isTeeTask(chainTaskId)).thenReturn(false);
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output/iexec_out");

        String hash = resultService.getTaskDeterminismHash(chainTaskId);
        // should not be equal to the content of the file since it is not a byte32
        assertThat(hash).isNotEqualTo("dummyRandomString");
    }

    @Test
    public void shouldReadSconeEnclaveSignatureFile(){
        String chainTaskId = "scone-tee";
        String expectedResult = "0xc746143d64ef1a1f9e280cee70e2866daad3116bfe0e7028a53e500b2c92a6d6";
        String expectedHash = "0x5ade3c39f9e83db590cbcb03fee7e0ba6c533fa3fb4e72f9320c3e641e38c31e";
        String expectedSeal = "0x5119fb3770cc545ff3ab0377842ebcd923a3cc02fc4390c285f5368e2b0f3742";
        String expectedSign = "0xa025ac611f80112c4827f316f2babd92d983c4ebcd4fdcebc57a6f02fd587c4d503264885f0c5aceeccac04c0f6257831bff57890786ceb01dcb9d191a788d711b";

        when(iexecHubService.isTeeTask(chainTaskId)).thenReturn(true);
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output/iexec_out");

        Optional<SconeEnclaveSignatureFile> oSconeEnclaveSignatureFile =
                resultService.readSconeEnclaveSignatureFile(chainTaskId);

        assertThat(oSconeEnclaveSignatureFile.isPresent()).isTrue();
        SconeEnclaveSignatureFile enclaveSignatureFile = oSconeEnclaveSignatureFile.get();

        assertThat(enclaveSignatureFile.getResult()).isEqualTo(expectedResult);
        assertThat(enclaveSignatureFile.getResultHash()).isEqualTo(expectedHash);
        assertThat(enclaveSignatureFile.getResultSalt()).isEqualTo(expectedSeal);
        assertThat(enclaveSignatureFile.getSignature()).isEqualTo(expectedSign);
    }

    @Test
    public void shouldNotReadSconeEnclaveSignatureSinceFileCorrupted() {
        String chainTaskId = "scone-tee-corrupted-file";

        when(iexecHubService.isTeeTask(chainTaskId)).thenReturn(true);
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output/iexec_out");

        Optional<SconeEnclaveSignatureFile> oSconeEnclaveSignatureFile =
                resultService.readSconeEnclaveSignatureFile(chainTaskId);

        assertThat(oSconeEnclaveSignatureFile.isPresent()).isFalse();
    }

    @Test
    public void shouldNotReadSconeEnclaveSignatureSinceFileMissing() {
        String chainTaskId = "scone-tee";

        when(iexecHubService.isTeeTask(chainTaskId)).thenReturn(true);
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/fakeFolder");

        Optional<SconeEnclaveSignatureFile> oSconeEnclaveSignatureFile =
                resultService.readSconeEnclaveSignatureFile(chainTaskId);

        assertThat(oSconeEnclaveSignatureFile.isPresent()).isFalse();
    }

    @Test
    public void shouldGetCallbackDataFromFile(){
        String chainTaskId = "callback";
        String expected = "0x0000000000000000000000000000000000000000000000000000016a0caa81920000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000004982f5d9a7000000000000000000000000000000000000000000000000000000000000000094254432d5553442d390000000000000000000000000000000000000000000000";
        when(workerConfigurationService.getTaskIexecOutDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output/iexec_out");
        String callbackDataString = resultService.getCallbackDataFromFile(chainTaskId);
        assertThat(callbackDataString).isEqualTo(expected);
    }

    @Test
    public void shouldNotGetCallbackDataSinceNotHexa(){
        String chainTaskId = "callback-fake";
        when(workerConfigurationService.getTaskOutputDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output");
        String callbackDataString = resultService.getCallbackDataFromFile(chainTaskId);
        assertThat(callbackDataString).isEqualTo("");
    }

    @Test
    public void shouldNotGetCallbackDataSinceNoFile(){
        String chainTaskId = "fake2";
        when(workerConfigurationService.getTaskOutputDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output");
        String callbackDataString = resultService.getCallbackDataFromFile(chainTaskId);
        assertThat(callbackDataString).isEqualTo("");
    }

    @Test
    public void shouldNotGetCallbackDataSinceChainTaskIdMissing(){
        String chainTaskId = "";
        when(workerConfigurationService.getTaskOutputDir(chainTaskId))
                .thenReturn(IEXEC_WORKER_TMP_FOLDER + "/" + chainTaskId + "/output");
        String callbackDataString = resultService.getCallbackDataFromFile(chainTaskId);
        assertThat(callbackDataString).isEqualTo("");
    }


}
