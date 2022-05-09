package io.openraven.securityrules.version;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Simple class to expose the Maven artifact version
 */
public class SecurityRulesVersion {

    /**
     *  Looks up the Maven version from META-INF
     * @return the runtime artifact version or UNKNONW
     */
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
