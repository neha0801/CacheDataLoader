package com.example.cacheloader;

import com.example.cacheloader.cache.BatchingCacheLoader;
import com.example.cacheloader.cache.CacheWriter;
import com.example.cacheloader.cache.CoherenceCacheWriter;
import com.example.cacheloader.config.LoaderProperties;
import com.example.cacheloader.reader.RecordReader;
import com.example.cacheloader.reader.RecordReaderFactory;
import com.tangosol.net.NamedCache;
import com.tangosol.net.Session;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Component;

/** Runs the configured load once at startup. */
@Component
public class CacheLoadRunner implements ApplicationRunner {

  private static final Logger log = LoggerFactory.getLogger(CacheLoadRunner.class);

  private final LoaderProperties properties;
  private final RecordReaderFactory readerFactory;
  private final ResourceLoader resourceLoader;
  private final Session session;
  private final ConfigurableApplicationContext context;

  public CacheLoadRunner(
      LoaderProperties properties,
      RecordReaderFactory readerFactory,
      ResourceLoader resourceLoader,
      Session session,
      ConfigurableApplicationContext context) {
    this.properties = properties;
    this.readerFactory = readerFactory;
    this.resourceLoader = resourceLoader;
    this.session = session;
    this.context = context;
  }

  @Override
  public void run(ApplicationArguments args) {
    Resource source = resolveSource(properties.getSource());
    if (!source.exists()) {
      throw new IllegalStateException("Source not found: " + properties.getSource());
    }

    log.info(
        "Loading {} into cache '{}' as {} (batch size {})",
        properties.getSource(),
        properties.getCacheName(),
        properties.getFormat(),
        properties.getBatchSize());

    RecordReader reader = readerFactory.forFormat(properties.getFormat());
    NamedCache<Object, Object> cache = session.getCache(properties.getCacheName());
    BatchingCacheLoader loader =
        new BatchingCacheLoader(properties.getKeyField(), properties.getBatchSize());

    long start = System.nanoTime();
    long loaded;
    try (Stream<Map<String, Object>> records = reader.read(source);
        CacheWriter writer = new CoherenceCacheWriter(cache)) {
      loaded = loader.load(records, writer);
    } catch (IOException e) {
      throw new UncheckedIOException("Failed to read " + properties.getSource(), e);
    }

    log.info(
        "Loaded {} entries into '{}' in {} ms",
        loaded,
        properties.getCacheName(),
        (System.nanoTime() - start) / 1_000_000);

    if (!properties.isKeepAlive()) {
      System.exit(SpringApplication.exit(context, () -> 0));
    }
  }

  /**
   * Resolves the source. A bare filesystem path would otherwise be read as a classpath resource, so
   * mark absolute paths explicitly.
   */
  private Resource resolveSource(String source) {
    boolean hasScheme = source.contains(":");
    String location = (!hasScheme && source.startsWith("/")) ? "file:" + source : source;
    return resourceLoader.getResource(location);
  }
}
