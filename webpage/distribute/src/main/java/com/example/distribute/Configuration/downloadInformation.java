package com.example.distribute.Configuration;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record downloadInformation(int waitTime, String downloadPath, int dropCount) { }
