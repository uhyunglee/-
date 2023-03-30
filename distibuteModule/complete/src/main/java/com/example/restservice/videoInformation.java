package com.example.restservice;



import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;


@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
public class videoInformation {
    private int frameWeight= 0;
    private int frameHeight;
    private int frameCount;
    private double fps;
    private double videoLength;
}
