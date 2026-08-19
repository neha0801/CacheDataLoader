package com.example.cacheloader.config;

import com.tangosol.net.Coherence;
import com.tangosol.net.CoherenceConfiguration;
import com.tangosol.net.Session;
import com.tangosol.net.SessionConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Starts a Coherence cluster member and exposes its session. */
@Configuration
public class CoherenceConfig {

  @Bean(destroyMethod = "close")
  public Coherence coherence(CoherenceProperties properties) {
    String cacheConfig = stripClasspathPrefix(properties.getCacheConfig());

    // Coherence reads these on start; they must be set before the member boots.
    System.setProperty("coherence.cluster", properties.getCluster());
    System.setProperty("coherence.cacheconfig", cacheConfig);

    SessionConfiguration session = SessionConfiguration.builder().withConfigUri(cacheConfig).build();
    Coherence coherence =
        Coherence.clusterMember(CoherenceConfiguration.builder().withSession(session).build());
    coherence.start().join();
    return coherence;
  }

  @Bean
  public Session coherenceSession(Coherence coherence) {
    return coherence.getSession();
  }

  /** Coherence resolves config URIs against the classpath itself, so drop Spring's prefix. */
  private static String stripClasspathPrefix(String configUri) {
    return configUri.startsWith("classpath:") ? configUri.substring("classpath:".length()) : configUri;
  }
}
