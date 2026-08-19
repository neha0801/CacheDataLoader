package com.example.cacheloader.cache;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** In-memory {@link CacheWriter} that remembers each batch it was handed. */
public class RecordingCacheWriter implements CacheWriter {

  private final List<Integer> batchSizes = new ArrayList<>();
  private final Map<Object, Object> contents = new LinkedHashMap<>();
  private boolean closed;

  @Override
  public void putAll(Map<Object, Object> batch) {
    batchSizes.add(batch.size());
    // Copy: the loader reuses and clears its batch map.
    contents.putAll(new HashMap<>(batch));
  }

  @Override
  public void close() {
    closed = true;
  }

  public List<Integer> batchSizes() {
    return batchSizes;
  }

  public Map<Object, Object> contents() {
    return contents;
  }

  public boolean isClosed() {
    return closed;
  }
}
