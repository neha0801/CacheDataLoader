package com.example.cacheloader.config;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

/** Settings for a single load run, bound from the {@code loader.*} keys. */
@Validated
@ConfigurationProperties(prefix = "loader")
public class LoaderProperties {

  public enum Format {
    CSV,
    JSON
  }

  /** Name of the Coherence cache to load into. */
  @NotBlank private String cacheName;

  /** Format of the source file. */
  private Format format = Format.CSV;

  /** Source file. Use a {@code classpath:} prefix for resources, or a filesystem path. */
  @NotBlank private String source;

  /** Number of entries per putAll call. */
  @Min(1)
  private int batchSize = 1000;

  /** Field in each record to use as the cache key. */
  @NotBlank private String keyField = "id";

  /** Keep the JVM running after the load finishes, rather than exiting. */
  private boolean keepAlive = false;

  public String getCacheName() {
    return cacheName;
  }

  public void setCacheName(String cacheName) {
    this.cacheName = cacheName;
  }

  public Format getFormat() {
    return format;
  }

  public void setFormat(Format format) {
    this.format = format;
  }

  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public int getBatchSize() {
    return batchSize;
  }

  public void setBatchSize(int batchSize) {
    this.batchSize = batchSize;
  }

  public String getKeyField() {
    return keyField;
  }

  public void setKeyField(String keyField) {
    this.keyField = keyField;
  }

  public boolean isKeepAlive() {
    return keepAlive;
  }

  public void setKeepAlive(boolean keepAlive) {
    this.keepAlive = keepAlive;
  }
}
