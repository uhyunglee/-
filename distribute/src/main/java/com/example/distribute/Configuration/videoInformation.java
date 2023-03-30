package com.example.distribute.Configuration;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record videoInformation(int frameWeight, int frameHeight, int frameCount, double fps, double videoLength) { }