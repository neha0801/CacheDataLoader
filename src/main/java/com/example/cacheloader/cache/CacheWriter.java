package com.example.cacheloader.cache;

import java.util.Map;

/**
 * Destination for loaded records. Keeps {@link BatchingCacheLoader} independent of Coherence so the
 * batching logic can be tested without a cluster.
 */
public interface CacheWriter extends AutoCloseable {

  /** Writes one batch. */
  void putAll(Map<Object, Object> batch);

  @Override
  void close();
}
