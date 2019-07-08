package com.iexec.worker.tee.scone;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.security.Signature;
import com.iexec.common.sms.scone.SconeSecureSessionResponse;
import com.iexec.common.sms.scone.SconeSecureSessionResponse.SconeSecureSession;
import com.iexec.common.utils.BytesUtils;
import com.iexec.worker.config.PublicConfigurationService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.sms.SmsService;

import static com.iexec.worker.chain.ContributionService.computeResultHash;
import static org.assertj.core.api.Java6Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

import static com.iexec.worker.chain.ContributionService.computeResultSeal;


public class SconeTeeServiceTests {

    public static final String FSPF_FILENAME = "volume.fspf";
    public static final String BENEFICIARY_KEY_FILENAME = "public.key";
    public static final String CHAIN_TASK_ID = "0xabc";

    @Rule public TemporaryFolder jUnitTemporaryFolder = new TemporaryFolder();

    @Mock private SconeLasConfiguration sconeLasConfiguration;
    @Mock private WorkerConfigurationService workerConfigurationService;
    @Mock private PublicConfigurationService publicConfigurationService;
    @Mock private SmsService smsService;

    @InjectMocks
    private SconeTeeService sconeTeeService;

    @Before
    public void beforeEach() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    public void shouldCreateSconeSecureSession() throws IOException {
        String sessionId = "randomSessionId";
        String sconeVolumeFspf = "NU6tRbysDhboPK8P6cQgnA=="; // base64 random string
        String beneficiaryKey = "key";
        SconeSecureSession session = new SconeSecureSessionResponse()
                .new SconeSecureSession(sessionId, sconeVolumeFspf, beneficiaryKey);

        String tmpFolderName = "tmp-folder";
        File tmpFolder = jUnitTemporaryFolder.newFolder(tmpFolderName);
        String tmpFolderPath = tmpFolder.getAbsolutePath();
        String fspfFilePath = tmpFolderPath + File.separator + FSPF_FILENAME;
        String keyFilePath = tmpFolderPath + File.separator + BENEFICIARY_KEY_FILENAME;

        ContributionAuthorization contributionAuth = ContributionAuthorization.builder()
                .chainTaskId(CHAIN_TASK_ID)
                .build();

        when(smsService.getSconeSecureSession(contributionAuth)).thenReturn(Optional.of(session));
        when(workerConfigurationService.getTaskSconeDir(CHAIN_TASK_ID)).thenReturn(tmpFolderPath);
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(tmpFolderPath);

        String returnedSessionId = sconeTeeService.createSconeSecureSession(contributionAuth);
        List<String> lines = Files.readAllLines(Paths.get(keyFilePath));

        assertThat(new File(fspfFilePath)).exists();
        assertThat(new File(keyFilePath)).exists();
        assertThat(returnedSessionId).isEqualTo(sessionId);
        assertThat(lines.get(0)).isEqualTo(beneficiaryKey);
    }

    @Test
    public void shouldNotCreateSconeSecureSessionSinceEmptySmsResponse() throws IOException {
        String tmpFolderName = "tmp-folder";
        File tmpFolder = jUnitTemporaryFolder.newFolder(tmpFolderName);
        String tmpFolderPath = tmpFolder.getAbsolutePath();
        String fspfFilePath = tmpFolderPath + File.separator + FSPF_FILENAME;
        String keyFilePath = tmpFolderPath + File.separator + BENEFICIARY_KEY_FILENAME;

        ContributionAuthorization contributionAuth = ContributionAuthorization.builder()
                .chainTaskId(CHAIN_TASK_ID)
                .build();

        when(smsService.getSconeSecureSession(contributionAuth)).thenReturn(Optional.empty());
        when(workerConfigurationService.getTaskSconeDir(CHAIN_TASK_ID)).thenReturn(tmpFolderPath);
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(tmpFolderPath);

        String returnedSessionId = sconeTeeService.createSconeSecureSession(contributionAuth);

        assertThat(new File(fspfFilePath)).doesNotExist();
        assertThat(new File(keyFilePath)).doesNotExist();
        assertThat(returnedSessionId).isEmpty();
    }

    @Test
    public void ShouldIsEnclaveSignatureValidBeTrue() {
        String chainTaskId = "0x1566a9348a284d12f7d81fa017fbc440fd501ddef5746821860ffda7113eb847";
        String worker = "0x1a69b2eb604db8eba185df03ea4f5288dcbbd248";
        String deterministHash = "0xb7e58c9d6fbde4420e87af44786ec46c797123d0667b72920b4cead23d60188b";

        String resultHash = computeResultHash(chainTaskId, deterministHash);
        String resultSeal = computeResultSeal(worker, chainTaskId, deterministHash);

        String enclaveAddress = "0x3cB738D98D7A70e81e81B0811Fae2452BcA049Bc";

        String r = "0xfe0d8948ca8739b0926ed5729532686b283755a1c1e660abf1ebd6362d1545c8";
        String s = "0x14e53d7cd66ec0a1cfe330b1e16e460ae354d33fb84cf9d62213b10c109f0db5";
        int v = 27;

        Signature enclaveSignature = new Signature(BytesUtils.stringToBytes(r), BytesUtils.stringToBytes(s), (byte) v);

        assertThat(sconeTeeService.isEnclaveSignatureValid(resultHash, resultSeal, enclaveSignature, enclaveAddress)).isTrue();
    }

    @Test
    public void ShouldIsEnclaveSignatureValidBeFalse() {
        String chainTaskId = "0x1566a9348a284d12f7d81fa017fbc440fd501ddef5746821860ffda7113eb847";
        String worker = "0x1a69b2eb604db8eba185df03ea4f5288dcbbd248";
        String deterministHash = "wrong hash";

        String resultHash = computeResultHash(chainTaskId, deterministHash);
        String resultSeal = computeResultSeal(worker, chainTaskId, deterministHash);

        String enclaveAddress = "0x3cB738D98D7A70e81e81B0811Fae2452BcA049Bc";

        String r = "0xfe0d8948ca8739b0926ed5729532686b283755a1c1e660abf1ebd6362d1545c8";
        String s = "0x14e53d7cd66ec0a1cfe330b1e16e460ae354d33fb84cf9d62213b10c109f0db5";
        int v = 27;

        Signature enclaveSignature = new Signature(BytesUtils.stringToBytes(r), BytesUtils.stringToBytes(s), (byte) v);

        assertThat(sconeTeeService.isEnclaveSignatureValid(resultHash, resultSeal, enclaveSignature, enclaveAddress)).isFalse();
    }
}