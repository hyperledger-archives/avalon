package com.iexec.worker.utils;


public class LoggingUtils {

    public static void printHighlightedMessage(String message) {
        String hashtagSequence = new String(new char[message.length()]).replace('\0', '#');
        String spaceSequence   = new String(new char[message.length()]).replace('\0', ' ');

        System.out.println();
        System.out.println("##" +   hashtagSequence    + "##");
        System.out.println("# " +    spaceSequence     + " #");
        System.out.println("# " +       message        + " #");
        System.out.println("# " +    spaceSequence     + " #");
        System.out.println("##" +   hashtagSequence    + "##");
        System.out.println();
    }
}