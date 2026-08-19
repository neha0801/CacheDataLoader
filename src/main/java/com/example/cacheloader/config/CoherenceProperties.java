package com.example.cacheloader.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** Cluster settings, bound from the {@code coherence.*} keys. */
@ConfigurationProperties(prefix = "coherence")
public class CoherenceProperties {

  /** Cluster to join. */
  private String cluster = "demo-cluster";

  /** Cache configuration descriptor passed to Coherence. */
  private String cacheConfig = "coherence-cache-config.xml";

  public String getCluster() {
    return cluster;
  }

  public void setCluster(String cluster) {
    this.cluster = cluster;
  }

  public String getCacheConfig() {
    return cacheConfig;
  }

  public void setCacheConfig(String cacheConfig) {
    this.cacheConfig = cacheConfig;
  }
}
