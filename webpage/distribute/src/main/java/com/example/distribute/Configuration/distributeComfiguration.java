package com.example.distribute.Configuration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class distributeComfiguration {
    @Bean
    public Mode mode(){
        return new Mode();
    }
}
