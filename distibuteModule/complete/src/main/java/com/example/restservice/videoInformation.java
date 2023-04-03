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
    private double frameWidth;
    private double frameHeight;
    private double frameCount;
    private double fps;
    private double videoLength;

}
