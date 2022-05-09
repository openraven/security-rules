package io.openraven.securityrules.version;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class SecurityRulesVersion {

    public synchronized String getVersion() {
        String version = "UNKNOWN";

        try (InputStream is = getClass().getResourceAsStream("/META-INF/maven/io.openraven.magpie/security-rules/pom.properties")) {
            Properties p = new Properties();
            if (is != null) {
                p.load(is);
                version = p.getProperty("version", "");
            }
        } catch (IOException e) {
            // not important, just return unknown;
        }

        return version;
    }
}
