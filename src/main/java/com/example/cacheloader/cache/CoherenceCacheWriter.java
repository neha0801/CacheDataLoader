package com.example.cacheloader.cache;

import com.tangosol.net.NamedCache;
import java.util.Map;

/** Writes batches into a Coherence {@link NamedCache}. */
public class CoherenceCacheWriter implements CacheWriter {

  private final NamedCache<Object, Object> cache;

  public CoherenceCacheWriter(NamedCache<Object, Object> cache) {
    this.cache = cache;
  }

  @Override
  public void putAll(Map<Object, Object> batch) {
    cache.putAll(batch);
  }

  @Override
  public void close() {
    cache.release();
  }
}
