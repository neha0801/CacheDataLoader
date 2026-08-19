package com.example.cacheloader.cache;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Drains a stream of records into a {@link CacheWriter}, keyed on one field and flushed in
 * fixed-size batches.
 */
public class BatchingCacheLoader {

  private static final Logger log = LoggerFactory.getLogger(BatchingCacheLoader.class);

  private final String keyField;
  private final int batchSize;

  public BatchingCacheLoader(String keyField, int batchSize) {
    if (keyField == null || keyField.isBlank()) {
      throw new IllegalArgumentException("keyField must not be blank");
    }
    if (batchSize < 1) {
      throw new IllegalArgumentException("batchSize must be at least 1, got " + batchSize);
    }
    this.keyField = keyField;
    this.batchSize = batchSize;
  }

  /**
   * Loads every record and returns how many entries were written.
   *
   * <p>Records sharing a key overwrite one another, matching cache semantics.
   */
  public long load(Stream<Map<String, Object>> records, CacheWriter writer) {
    Map<Object, Object> batch = new HashMap<>();
    long written = 0;
    long rowNumber = 0;

    for (Iterator<Map<String, Object>> it = records.iterator(); it.hasNext(); ) {
      Map<String, Object> record = it.next();
      rowNumber++;

      Object key = record.get(keyField);
      if (key == null) {
        throw new IllegalStateException(
            "Record %d has no value for key field '%s'; available fields: %s"
                .formatted(rowNumber, keyField, record.keySet()));
      }

      batch.put(key, record);
      if (batch.size() >= batchSize) {
        written += flush(batch, writer);
      }
    }
    written += flush(batch, writer);

    log.info("Loaded {} entries from {} records", written, rowNumber);
    return written;
  }

  private long flush(Map<Object, Object> batch, CacheWriter writer) {
    if (batch.isEmpty()) {
      return 0;
    }
    int size = batch.size();
    writer.putAll(batch);
    log.debug("Flushed batch of {}", size);
    batch.clear();
    return size;
  }
}
