package com.example.cacheloader;

import com.example.cacheloader.config.CoherenceProperties;
import com.example.cacheloader.config.LoaderProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties({LoaderProperties.class, CoherenceProperties.class})
public class CacheDataLoaderApplication {

  public static void main(String[] args) {
    SpringApplication.run(CacheDataLoaderApplication.class, args);
  }
}
