package com.example.distribute.restAPI;

import com.example.distribute.Configuration.ConversionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RESTConversionController {

    private final ConversionService conversionService;

    @Autowired
    public RESTConversionController(ConversionService conversionService) {
        this.conversionService = conversionService;
    }

    @GetMapping("/distribution/download")
    public ResponseEntity<String> checkConversionStatus() {
        conversionService.setConversionStatus("completed");
        String conversionStatus = conversionService.getConversionStatus();
        System.out.println("/distribution/download");
        // conversionStatus 사용

        if (conversionStatus!=null) {
            return ResponseEntity.ok(conversionStatus);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Conversion status not found");
        }
    }

    @GetMapping("/status/conversion")
    public ResponseEntity<String> getConversionStatus(){
        String conversionStatus = conversionService.getConversionStatus();
//        System.out.println(conversionStatus);
        if (conversionStatus != null) {
            return ResponseEntity.ok(conversionStatus);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Conversion status not found");
        }
    }


}
