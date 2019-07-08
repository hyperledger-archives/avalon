package com.iexec.worker.utils;

import org.apache.commons.io.FileUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.MockitoAnnotations;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import static com.iexec.worker.utils.FileHelper.downloadFileInDirectory;
import static org.assertj.core.api.Assertions.assertThat;

public class FileHelperTests {

    private static final String TEST_FOLDER = "/tmp/iexec-test";

    // clean the test repo before and after each test
    @Before
    public void init() throws IOException {
        MockitoAnnotations.initMocks(this);
        FileUtils.deleteDirectory(new File(TEST_FOLDER));
    }

    @After
    public void tearDown() throws IOException {
        FileUtils.deleteDirectory(new File(TEST_FOLDER));
    }

    @Test(expected = Exception.class)
    public void shouldThrowExceptionWhenInvokingConstructor() throws Exception {
        Constructor<FileHelper> clazz = FileHelper.class.getDeclaredConstructor();
        clazz.setAccessible(true);
        // calling the private constructor
        clazz.newInstance();
    }


    @Test
    public void shouldCreateFileWithContent() throws IOException {
        String data = "a test";
        File file = FileHelper.createFileWithContent(TEST_FOLDER + "/test.txt", data);
        assertThat(file).isNotNull();
        assertThat(file).exists();
        assertThat(file).isFile();
        String content = new String(Files.readAllBytes(Paths.get(file.getAbsolutePath())), StandardCharsets.UTF_8);
        assertThat(content).isEqualTo(data);
    }

    @Test
    public void shouldCreateFolder() {
        String folderPath = TEST_FOLDER + "/folder";
        boolean created = FileHelper.createFolder(folderPath);
        File newFolder = new File(folderPath);
        assertThat(created).isTrue();
        assertThat(newFolder).isNotNull();
        assertThat(newFolder).exists();
        assertThat(newFolder).isDirectory();

        // it should not change anything if the folder is already created
        boolean createdAgain = FileHelper.createFolder(folderPath);
        File existingFolder = new File(folderPath);
        assertThat(createdAgain).isTrue();
        assertThat(existingFolder).isNotNull();
        assertThat(existingFolder).exists();
        assertThat(existingFolder).isDirectory();
    }

    @Test
    public void shouldCreateFolderRecursively() {
        String folderPath = TEST_FOLDER + "/folder1/folder2/folder3";
        boolean created = FileHelper.createFolder(folderPath);
        File newFolder = new File(folderPath);
        assertThat(created).isTrue();
        assertThat(newFolder).isNotNull();
        assertThat(newFolder).exists();
        assertThat(newFolder).isDirectory();

        // it should not change anything if the folder is already created
        boolean createdAgain = FileHelper.createFolder(folderPath);
        File existingFolder = new File(folderPath);
        assertThat(createdAgain).isTrue();
        assertThat(existingFolder).isNotNull();
        assertThat(existingFolder).exists();
        assertThat(existingFolder).isDirectory();
    }

    @Test
    public void shouldDeleteFile() {
        String filePath = TEST_FOLDER + "/test.txt";
        File file = FileHelper.createFileWithContent(filePath, "Hello world");
        assertThat(file).isNotNull();
        assertThat(file).exists();
        assertThat(file).isFile();

        boolean isDeleted = FileHelper.deleteFile(filePath);
        File deletedFile = new File(filePath);
        assertThat(isDeleted).isTrue();
        assertThat(deletedFile).doesNotExist();
    }

    @Test
    public void shouldNotDeleteNonExistingFile() {
        String filePath = TEST_FOLDER + "/test.txt";

        boolean isDeleted = FileHelper.deleteFile(filePath);
        File deletedFile = new File(filePath);
        assertThat(isDeleted).isFalse();
        assertThat(deletedFile).doesNotExist();
    }

    @Test
    public void shouldDeleteFolder() {
        String folderPath = TEST_FOLDER + "/folder";
        boolean created = FileHelper.createFolder(folderPath);
        File newFolder = new File(folderPath);
        assertThat(created).isTrue();
        assertThat(newFolder).isNotNull();
        assertThat(newFolder).exists();
        assertThat(newFolder).isDirectory();

        boolean isDeleted = FileHelper.deleteFolder(folderPath);
        File deletedFolder = new File(folderPath);
        assertThat(isDeleted).isTrue();
        assertThat(deletedFolder).doesNotExist();
    }

    @Test
    public void shouldDeleteFoldersRecursively() {
        String folderPath = TEST_FOLDER + "/folder1/folder2/folder3";
        boolean created = FileHelper.createFolder(folderPath);
        File newFolder = new File(folderPath);
        assertThat(created).isTrue();
        assertThat(newFolder).isNotNull();
        assertThat(newFolder).exists();
        assertThat(newFolder).isDirectory();

        boolean isDeleted = FileHelper.deleteFolder(folderPath);
        File deletedFolder = new File(folderPath);
        assertThat(isDeleted).isTrue();
        assertThat(deletedFolder).doesNotExist();
    }

    @Test
    public void shouldNotDeleteNonExistingFolder() {
        String folderPath = TEST_FOLDER + "/folder";
        boolean isDeleted = FileHelper.deleteFolder(folderPath);
        File deletedFolder = new File(folderPath);
        assertThat(isDeleted).isFalse();
        assertThat(deletedFolder).doesNotExist();
    }

    @Test
    public void shouldZipFolder() {
        FileHelper.createFileWithContent(TEST_FOLDER + "/taskId/test.txt", "a test");
        File zipFile = FileHelper.zipFolder(TEST_FOLDER + "/taskId");
        assertThat(zipFile).isNotNull();
        assertThat(zipFile).exists();
        assertThat(zipFile).isFile();
        assertThat(zipFile.getAbsolutePath()).isEqualTo(TEST_FOLDER + "/taskId.zip");
    }

    @Test
    public void shouldDownloadFile() {
        //TODO 1 - Try https resources: https://iex.ec/wp-content/uploads/2018/12/token.svg
        //TODO 2- Try resources with redirection: https://goo.gl/t8JxoX
        String fileUri = "http://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/512/iExec-RLC-RLC-icon.png";
        boolean isFileDownloaded = downloadFileInDirectory(fileUri, TEST_FOLDER);
        assertThat(isFileDownloaded).isTrue();
        assertThat(new File(TEST_FOLDER + "/" + Paths.get(fileUri).getFileName().toString())).exists();
    }

    @Test
    public void shouldNotDownloadFileSinceEmptyUri() {
        String fileUri = "";
        boolean isFileDownloaded = downloadFileInDirectory(fileUri, TEST_FOLDER);
        assertThat(isFileDownloaded).isFalse();
    }

    @Test
    public void shouldNotDownloadFileSinceDummyUri() {
        String fileUri = "http://dummy-uri";
        boolean isFileDownloaded = downloadFileInDirectory(fileUri, TEST_FOLDER);
        assertThat(isFileDownloaded).isFalse();
    }

}
