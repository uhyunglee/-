package com.example.restservice;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.scheduling.annotation.Async;

import java.io.*;


@RestController
public class videoDistributeController {
	@GetMapping("/videoinformation")
	public static videoInformation returnVideoInformation() throws  IOException,InterruptedException {
		Runnable r = () -> {
			ProcessBuilder pb = new ProcessBuilder("python", "C:/Users/Public/test.py");
			pb.redirectErrorStream(true);
			try {
				Process process = pb.start();
				String line;
				BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
				while ((line = reader.readLine()) != null) {
					System.out.println(line);
				}
				int exitCode = process.waitFor();
				System.out.println("Exited with error code " + exitCode);
			} catch (IOException  | InterruptedException e ) {
				e.printStackTrace();
			}

		};
		Thread t = new Thread(r);
		t.start();
		ProcessBuilder pb = new ProcessBuilder("python", "C:/Users/Public/videoinformation.py");
		pb.redirectErrorStream(true);
		Process process = pb.start();

		BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
		String line;
		double fps = 0.0;
		double width = 0;
		double height = 0;
		double totalFrames = 0;
		double videoLength=0.0;
		while ((line = reader.readLine()) != null) {
			System.out.println(line);
			String[] parts = line.split(": ");
			switch (parts[0]) {
				case "FPS" -> fps = Double.parseDouble(parts[1]);
				case "Width" -> width = Double.parseDouble(parts[1]);
				case "Height" -> height = Double.parseDouble(parts[1]);
				case "Total frames" -> totalFrames = Double.parseDouble(parts[1]);
				case "VideoLength" -> videoLength = Double.parseDouble(parts[1]);
			}
		}

		try {
			int exitCode = process.waitFor();
			System.out.println("Exited with error code " + exitCode);
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
			System.err.println("Interrupted while waiting for the process to finish.");
		}



		return videoInformation.builder()
				.frameWidth(width)
				.frameHeight(height)
				.frameCount(totalFrames)
				.fps(fps)
				.videoLength(videoLength)
				.build();
	}


}
