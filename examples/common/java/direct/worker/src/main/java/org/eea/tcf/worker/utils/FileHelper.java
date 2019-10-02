  /*****************************************************************************
  * Copyright 2019 iExec Blockchain Tech
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
  *****************************************************************************/
package org.eea.tcf.worker.utils;

import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

import java.io.*;
import java.net.URL;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

@Slf4j
public class FileHelper {

    public static final String OUT_DIR_PATH = File.separatorChar + "tcf_out";

    private FileHelper() {
        throw new UnsupportedOperationException();
    }

    public static File createFileWithContent(String filePath, String data) {
        return createFileWithContent(filePath, data.getBytes());
    }

    public static File createFileWithContent(String filePath, byte[] data) {
        String parentDirectoryPath = new File(filePath).getParent();
        boolean isParentFolderCreated = createFolder(parentDirectoryPath);

        if (!isParentFolderCreated) {
            log.error("Failed to create base directory [parentDirectoryPath:{}]",
                    parentDirectoryPath);
            return null;
        }

        try {
            Files.write(Paths.get(filePath), data);
            log.debug("File created [filePath:{}]", filePath);
            return new File(filePath);
        } catch (IOException e) {
            log.error("Failed to create file [filePath:{}]", filePath);
            return null;
        }
    }

    public static boolean downloadFileInDirectory(String fileUri,
                                                  String directoryPath) {
        if (!createFolder(directoryPath)) {
            log.error("Failed to create base directory [directoryPath:{}]",
                    directoryPath);
            return false;
        }

        if (fileUri.isEmpty()) {
            log.error("FileUri shouldn't be empty [fileUri:{}]", fileUri);
            return false;
        }

        InputStream in;
        try {
            //Not working with https resources yet
            in = new URL(fileUri).openStream();
        } catch (IOException e) {
            log.error("Failed to download file [fileUri:{}, exception:{}]",
                    fileUri, e.getCause());
            return false;
        }

        try {
            String fileName = Paths.get(fileUri).getFileName().toString();
            Files.copy(in,
                    Paths.get(directoryPath + File.separator + fileName),
                    StandardCopyOption.REPLACE_EXISTING);
            log.info("Downloaded data [fileUri:{}]", fileUri);
            return true;
        } catch (IOException e) {
            log.error("Failed to copy downloaded file to disk [directoryPath:{}," +
                            "fileUri:{}]", directoryPath, fileUri);
            return false;
        }
    }

    public static String downloadFileInString(URL url) {
        try {
            InputStream in = url.openStream();//Not working with https resources yet
            return new String(in.readAllBytes());
        } catch (IOException e) {
            log.error("Failed to download file [url:{}, exception:{}]", url,
                    e.getCause());
            return null;
        }
    }

    public static boolean createFolder(String folderPath) {
        File baseDirectory = new File(folderPath);
        return baseDirectory.exists() ? true : baseDirectory.mkdirs();
    }

    public static boolean deleteFile(String filePath) {
        try {
            Files.delete(Paths.get(filePath));
            log.info("File has been deleted [path:{}]", filePath);
            return true;
        } catch (IOException e) {
            log.error("Problem when trying to delete the file [path:{}]",
                    filePath);
        }
        return false;
    }

    public static boolean deleteFolder(String folderPath) {
        File folder = new File(folderPath);
        if (!folder.exists()) {
            log.info("Folder doesn't exist so can't be deleted [path:{}]",
                    folderPath);
            return false;
        }

        try {
            FileUtils.deleteDirectory(folder);
            log.info("Folder has been deleted [path:{}]", folderPath);
            return true;
        } catch (IOException e) {
            log.error("Problem when trying to delete the folder [path:{}]",
                    folderPath);
        }
        return false;
    }

    public static File zipFolder(String folderPath) {
        String zipFilePath = folderPath + ".zip";
        Path sourceFolderPath = Paths.get(folderPath);

        try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(new
                File(zipFilePath)))) {
            Files.walkFileTree(sourceFolderPath,
                    new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file,
                                                 BasicFileAttributes attrs)
                        throws IOException {
                    log.debug("Adding file to zip [file:{}, zip:{}]",
                            file.toAbsolutePath().toString(), zipFilePath);
                    zos.putNextEntry(new ZipEntry(
                            sourceFolderPath.relativize(file).toString()));
                    Files.copy(file, zos);
                    zos.closeEntry();
                    return FileVisitResult.CONTINUE;
                }
            });
            log.info("Folder zipped [path:{}]", zipFilePath);
            return new File(zipFilePath);

        } catch (Exception e) {
            log.error("Failed to zip folder [path:{}]", zipFilePath);
        }
        return null;
    }

    public static boolean replaceFile(String toBeReplaced, String replacer) {
        try {
            Files.delete(Paths.get(toBeReplaced));
            return new File(replacer).renameTo(new File(toBeReplaced));
        } catch (IOException e) {
            log.error("Problem when trying to replace file [toBeReplaced:{}, replacer:{}]",
                    toBeReplaced, replacer);
            e.printStackTrace();
            return false;
        }
    }

    public static String getFilenameFromUri(String uri) {
        return Paths.get(uri).getFileName().toString();
    }

    public static String readZippedFileInString(@NonNull String path) {
        return readFileInString(path, true);
    }

    public static String readFileInString(@NonNull String path) {
        return readFileInString(path, false);
    }

    public static String readFileInString(@NonNull String path, boolean zipped) {
        StringBuffer sb = new StringBuffer();
        try {
            File f = new File(path);
            InputStream fis = new FileInputStream(f);

            if(zipped)
                fis = new ZipInputStream(fis);

            int fsize = (int) f.length();
            byte buffer[] = new byte[fsize];
            int read = -1;

            // Just in case the long to int cast overflew
            while((read = fis.read(buffer)) > 0)
                sb.append(new String(buffer));
            fis.close();

        } catch (Exception e) {
            log.error("Error reading file [path:{}, exception:{}]", path,
                    e.getMessage());
            System.exit(34);
        }

        return sb.toString();
    }
}
