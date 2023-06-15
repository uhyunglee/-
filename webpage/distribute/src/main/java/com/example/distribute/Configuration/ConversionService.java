package com.example.distribute.Configuration;
import org.springframework.stereotype.Service;

@Service
public class ConversionService {
    private String conversionStatus;


    public String getConversionStatus() {
        return conversionStatus;
    }

    public void setConversionStatus(String conversionStatus) {
        this.conversionStatus = conversionStatus;
    }

    // 변환 상태를 확인하는 로직 등의 비즈니스 로직을 구현할 수 있습니다.
}

