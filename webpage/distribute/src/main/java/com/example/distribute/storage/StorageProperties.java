package com.example.distribute.storage;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Service;

@ConfigurationProperties("storage")
@Service
public class StorageProperties {

    /**
     * Folder location for storing files
     */
    private String location = "/home/share/nfs";

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

}