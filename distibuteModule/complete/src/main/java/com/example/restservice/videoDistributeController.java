package com.example.restservice;

import org.springframework.web.bind.annotation.GetMapping;

import org.springframework.web.bind.annotation.RestController;

@RestController
public class videoDistributeController {
	@GetMapping("/videoinformation")
	public videoInformation returnVideoInformation() {
		videoInformation videoinformation = videoInformation.builder()
				.frameWeight(854)
				.frameHeight(480)
				.frameCount(179)
				.fps(29.97)
				.videoLength(5.972639)
				.build();


		return	videoinformation;
	}
}
